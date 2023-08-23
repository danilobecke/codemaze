from datetime import datetime, timedelta
from io import BytesIO
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from tests.helper import get_manager_id_token, get_student_id_token, get_random_student_token, get_new_group_id_code, join_group, create_task_json, create_test_case_json, post, CONTENT_TYPE_FORM_DATA, get, get_random_manager_token, set_up_task_id_student_token, patch

class TestReport:
    def __set_up_valid_3_open_3_closed_tests_manager_three_students_tests_task(self, starts_on: str | None = None, ends_on: str | None = None) -> tuple[str, str, str, str, list[str], str]:
        manager_token = get_manager_id_token()[1]
        student_token_one = get_student_id_token()[1]
        student_token_two = get_random_student_token('Z')
        student_token_three = get_random_student_token('A')
        group_id, code = get_new_group_id_code(None, manager_token)
        join_group(code, group_id, student_token_one, manager_token)
        join_group(code, group_id, student_token_two, manager_token)
        join_group(code, group_id, student_token_three, manager_token)
        task_id = create_task_json(manager_token, group_id, starts_on=starts_on, ends_on=ends_on)['id']
        tests: list[str] = []
        tests.append(create_test_case_json(manager_token, task_id, closed=False, content_in='1', content_out='1')['id'])
        tests.append(create_test_case_json(manager_token, task_id, closed=False, content_in='2', content_out='2')['id'])
        tests.append(create_test_case_json(manager_token, task_id, closed=False, content_in='3', content_out='3')['id'])
        tests.append(create_test_case_json(manager_token, task_id, closed=True, content_in='4', content_out='4')['id'])
        tests.append(create_test_case_json(manager_token, task_id, closed=True, content_in='5', content_out='5')['id'])
        tests.append(create_test_case_json(manager_token, task_id, closed=True, content_in='6', content_out='6')['id'])
        return (manager_token, student_token_one, student_token_two, student_token_three, tests, task_id)

    def __get_code_failing_tests(self, tests: list[int]) -> str:
        code = ''
        if len(tests) == 0:
            code = '''
#include<stdio.h>
int main() {
    int a;
    scanf("%d", &a);
    printf("%d", a);
    return 0;
}
'''
        else:
            condition_statement = ' || '.join([ f'a == {test}' for test in tests ])
            code = f'''
#include<stdio.h>
int main() {{
    int a;
    scanf("%d", &a);
    if({condition_statement}) {{
        printf("0");
    }}
    printf("%d", a);
    return 0;
}}
'''
        return code

    def __post_result_id(self, task_id: str, code: str, student_token: str) -> str:
        payload = {
            'code': (BytesIO(code.encode('utf-8')), 'code.c')
        }
        return str(post(f'/api/v1/tasks/{task_id}/results', payload, student_token, CONTENT_TYPE_FORM_DATA)[1]['id'])

    def test_get_report_download_code_all_success_first_attempt(self) -> None:
        manager_token, student_token_one, student_token_two, student_token_three, _, task_id = self.__set_up_valid_3_open_3_closed_tests_manager_three_students_tests_task()
        code = self.__get_code_failing_tests([])
        result_id_1 = self.__post_result_id(task_id, code, student_token_one) # Name: Student
        result_id_2 = self.__post_result_id(task_id, code, student_token_two) # Name: Z-random
        result_id_3 = self.__post_result_id(task_id, code, student_token_three) # Name: A-random
        results = [result_id_3, result_id_1, result_id_2]

        response = get(f'/api/v1/tasks/{task_id}/results', manager_token)

        assert response[0] == 200
        overall = response[1]['overall']
        students = response[1]['students']
        tests = response[1]['tests']

        assert overall['submissions_percentage'] == 100
        assert overall['mean_attempts_success_all'] == 1
        assert overall['tests_more_failures'] == []
        assert overall['plagiarism_report_urls'] == [] # the task has no ends_on set
        results_percentages = overall['results_percentages']
        assert len(results_percentages) == 1
        assert results_percentages[0]['result_percentage'] == 100
        assert results_percentages[0]['students_percentage'] == 100

        assert len(students) == 3
        for position, student in enumerate(students):
            assert student['name'] is not None
            assert student['open_result_percentage'] == 100
            assert student['closed_result_percentage'] == 100
            assert student['result_percentage'] == 100
            assert student['number_attempts'] == 1
            assert student['source_code_url'] == f'/api/v1/results/{results[position]}/code'
            assert student['wrong_tests_id'] == []

            response_get_code = get(student['source_code_url'], manager_token, decode_as_json=False)
            assert response_get_code[0] == 200
            assert str(response_get_code[1]) == code

        assert len(tests) == 6
        assert all(test['correct_percentage'] == 100 for test in tests)

    def test_get_report_without_any_submission(self) -> None:
        manager_token, *_, task_id = self.__set_up_valid_3_open_3_closed_tests_manager_three_students_tests_task()

        response = get(f'/api/v1/tasks/{task_id}/results', manager_token)

        assert response[0] == 200
        overall = response[1]['overall']
        students = response[1]['students']
        tests = response[1]['tests']

        assert overall['submissions_percentage'] == 0
        assert overall.get('mean_attempts_success_all') is None
        assert overall['tests_more_failures'] == []
        assert overall['plagiarism_report_urls'] == [] # the task has no ends_on set
        results_percentages = overall['results_percentages']
        assert len(results_percentages) == 1
        assert results_percentages[0]['result_percentage'] == 0
        assert results_percentages[0]['students_percentage'] == 100

        assert len(students) == 3
        for student in students:
            assert student['name'] is not None
            assert student['open_result_percentage'] == 0
            assert student['closed_result_percentage'] == 0
            assert student['result_percentage'] == 0
            assert student['number_attempts'] == 0
            assert student.get('source_code_url') is None
            assert student['wrong_tests_id'] == []

        assert len(tests) == 6
        assert all(test['correct_percentage'] == 0 for test in tests)

    # pylint: disable=too-many-statements
    @pytest.mark.smoke
    def test_get_report_download_code_with_mixed_results(self) -> None:
        manager_token, student_token_one, _, student_token_three, tests_ids, task_id = self.__set_up_valid_3_open_3_closed_tests_manager_three_students_tests_task(ends_on=(datetime.now().astimezone() + timedelta(days=1)).isoformat())
        code_failing_one_test = self.__get_code_failing_tests([3])
        code_success = self.__get_code_failing_tests([])
        code_failing = self.__get_code_failing_tests([4, 5])
        self.__post_result_id(task_id, code_failing_one_test, student_token_one)
        result_id_1 = self.__post_result_id(task_id, code_success, student_token_one) # Name: Student
        result_id_3 = self.__post_result_id(task_id, code_failing, student_token_three) # Name: A-random

        response = get(f'/api/v1/tasks/{task_id}/results', manager_token)

        failing_test_ids = [tests_ids[3], tests_ids[4]]

        assert response[0] == 200
        overall = response[1]['overall']
        students = response[1]['students']
        tests = response[1]['tests']

        assert overall['submissions_percentage'] == 66.67
        assert overall['mean_attempts_success_all'] == 2
        assert overall['tests_more_failures'] == failing_test_ids
        assert overall['plagiarism_report_urls'] == [] # the task is still open
        results_percentages = overall['results_percentages']
        assert len(results_percentages) == 3
        assert results_percentages[0]['result_percentage'] == 100
        assert results_percentages[0]['students_percentage'] == 33.33
        assert results_percentages[1]['result_percentage'] == 66.66
        assert results_percentages[1]['students_percentage'] == 33.33
        assert results_percentages[2]['result_percentage'] == 0
        assert results_percentages[2]['students_percentage'] == 33.33

        assert len(students) == 3
        assert students[0]['name'] is not None
        assert students[0]['open_result_percentage'] == 100
        assert students[0]['closed_result_percentage'] == 33.33
        assert students[0]['result_percentage'] == 66.66
        assert students[0]['number_attempts'] == 1
        assert students[0]['source_code_url'] == f'/api/v1/results/{result_id_3}/code'
        assert students[0]['wrong_tests_id'] == failing_test_ids
        response_get_code = get(students[0]['source_code_url'], manager_token, decode_as_json=False)
        assert response_get_code[0] == 200
        assert str(response_get_code[1]) == code_failing

        assert students[1]['name'] is not None
        assert students[1]['open_result_percentage'] == 100
        assert students[1]['closed_result_percentage'] == 100
        assert students[1]['result_percentage'] == 100
        assert students[1]['number_attempts'] == 2
        assert students[1]['source_code_url'] == f'/api/v1/results/{result_id_1}/code'
        assert students[1]['wrong_tests_id'] == []
        response_get_code = get(students[1]['source_code_url'], manager_token, decode_as_json=False)
        assert response_get_code[0] == 200
        assert str(response_get_code[1]) == code_success

        assert students[2]['name'] is not None
        assert students[2]['open_result_percentage'] == 0
        assert students[2]['closed_result_percentage'] == 0
        assert students[2]['result_percentage'] == 0
        assert students[2]['number_attempts'] == 0
        assert students[2].get('source_code_url') is None
        assert students[2]['wrong_tests_id'] == []

        assert len(tests) == 6
        assert tests[0]['correct_percentage'] == 100
        assert tests[1]['correct_percentage'] == 100
        assert tests[2]['correct_percentage'] == 100
        assert tests[3]['correct_percentage'] == 50
        assert tests[4]['correct_percentage'] == 50
        assert tests[5]['correct_percentage'] == 100

    def test_get_report_download_code_with_moss_report(self) -> None:
        request = Request('http://moss.stanford.edu', method='HEAD')
        try:
            with urlopen(request, timeout=1) as response:
                if response.status != 200:
                    # server down, skip test
                    assert True
                    return
        except HTTPError:
            assert True
            return
        manager_token, student_token_one, student_token_two, student_token_three, tests_ids, task_id = self.__set_up_valid_3_open_3_closed_tests_manager_three_students_tests_task(starts_on=(datetime.now().astimezone() - timedelta(days=2)).isoformat())
        code_failing_one_test = self.__get_code_failing_tests([4])
        code_success = self.__get_code_failing_tests([])
        code_failing = self.__get_code_failing_tests([4, 5])
        self.__post_result_id(task_id, code_failing_one_test, student_token_one)
        self.__post_result_id(task_id, code_success, student_token_two)
        self.__post_result_id(task_id, code_failing, student_token_three)
        # patch task to finished to generate a plagiarism report
        payload = {
            'ends_on': (datetime.now().astimezone() - timedelta(days=1)).isoformat(),
        }
        patch(f'/api/v1/tasks/{task_id}', payload, manager_token, CONTENT_TYPE_FORM_DATA)

        response = get(f'/api/v1/tasks/{task_id}/results', manager_token)

        assert response[0] == 200
        overall = response[1]['overall']

        assert overall['submissions_percentage'] == 100
        assert overall['mean_attempts_success_all'] == 1
        assert overall['tests_more_failures'] == [tests_ids[3]]
        assert len(overall['plagiarism_report_urls']) == 1
        url = overall['plagiarism_report_urls'][0]
        results_percentages = overall['results_percentages']
        assert len(results_percentages) == 3
        assert results_percentages[0]['result_percentage'] == 100
        assert results_percentages[0]['students_percentage'] == 33.33
        assert results_percentages[1]['result_percentage'] == 83.34
        assert results_percentages[1]['students_percentage'] == 33.33
        assert results_percentages[2]['result_percentage'] == 66.66
        assert results_percentages[2]['students_percentage'] == 33.33

        response_2 = get(f'/api/v1/tasks/{task_id}/results', manager_token)

        assert response_2[0] == 200
        overall2 = response_2[1]['overall']
        assert url == overall2['plagiarism_report_urls'][0] # should retrieve from database

    def test_get_report_with_non_manager_should_return_forbidden(self) -> None:
        manager_token = get_manager_id_token()[1]
        task_id = create_task_json(manager_token)['id']
        random_manager = get_random_manager_token()

        response = get(f'/api/v1/tasks/{task_id}/results', random_manager)
        assert response[0] == 403

    def test_get_report_with_student_should_return_unauthorized(self) -> None:
        manager_token = get_manager_id_token()[1]
        group_id, code = get_new_group_id_code(None, manager_token)
        student_token = get_student_id_token()[1]
        join_group(code, group_id, student_token, manager_token)
        task_id = create_task_json(manager_token, group_id)['id']

        response = get(f'/api/v1/tasks/{task_id}/results', student_token)
        assert response[0] == 401

    def test_get_report_with_invlaid_id_should_return_not_found(self) -> None:
        manager_token = get_manager_id_token()[1]

        response = get(f'/api/v1/tasks/{9999999}/results', manager_token)
        assert response[0] == 404

    def test_download_code_with_student_should_return_unauthorized(self) -> None:
        task_id, student_token = set_up_task_id_student_token()
        result_id = self.__post_result_id(task_id, 'code', student_token)

        response = get(f'/api/v1/results/{result_id}/code', student_token)
        assert response[0] == 401

    def test_download_code_with_non_manager_should_return_forbidden(self) -> None:
        task_id, student_token = set_up_task_id_student_token()
        result_id = self.__post_result_id(task_id, 'code', student_token)
        random_manager = get_random_manager_token()

        response = get(f'/api/v1/results/{result_id}/code', random_manager)
        assert response[0] == 403

    def test_download_code_with_invalid_id_should_return_not_found(self) -> None:
        manager_id = get_manager_id_token()[1]

        response = get(f'/api/v1/results/{9999999}/code', manager_id)
        assert response[0] == 404
