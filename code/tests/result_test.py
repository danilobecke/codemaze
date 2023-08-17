from datetime import datetime, timedelta
from io import BytesIO

import pytest

from tests.helper import post, get_manager_id_token, create_task_json, create_test_case_json, get_student_id_token, create_join_request_group_id, CONTENT_TYPE_FORM_DATA, get_filepath_of_size, get_new_group_id_code, get_random_name, get, patch

VALID_C_CODE = '''
#include<stdio.h>
int main() {
    int a, b;
    scanf("%d %d", &a, &b);
    printf("%d", a+b);
}
'''

INVALID_C_CODE = '''
int main() {
    printf("Invalid code - missing import.")
'''

TIMEOUT_C_CODE = '''
#include <unistd.h>
int main() {
    sleep(3);
}
'''

RUNTIME_ERROR_C_CODE = '''
#include<stdio.h>
int main() {
	fprintf(stderr, "%s", "Error");
}
'''

# pylint: disable=too-many-public-methods
class TestResult:
    def __set_up_task_id_student_token(self, starts_on: str | None = None, ends_on: str | None = None, max_attempts: int | None = None) -> tuple[str, str]:
        manager_token = get_manager_id_token()[1]
        student_token = get_student_id_token()[1]
        group_id = create_join_request_group_id(student_token, manager_token, approve=True)
        task_id = create_task_json(manager_token, group_id, starts_on=starts_on, ends_on=ends_on, max_attempts=max_attempts)['id']
        create_test_case_json(manager_token, task_id)
        return (task_id, student_token)

    def __set_up_valid_2_open_2_closed_tests_task_id_student_token(self) -> tuple[str, str]:
        manager_token = get_manager_id_token()[1]
        student_token = get_student_id_token()[1]
        group_id = create_join_request_group_id(student_token, manager_token, approve=True)
        task_id = create_task_json(manager_token, group_id)['id']
        create_test_case_json(manager_token, task_id, closed=False, content_in='1 2', content_out='3')
        create_test_case_json(manager_token, task_id, closed=False, content_in='3 4', content_out='7')
        create_test_case_json(manager_token, task_id, closed=True, content_in='5 6', content_out='11')
        create_test_case_json(manager_token, task_id, closed=True, content_in='7 8', content_out='15')
        return (task_id, student_token)

    def __set_up_result_source_code_url_student_token(self, code: str) -> tuple[str, str]:
        task_id, student_token = self.__set_up_task_id_student_token()
        payload = {
            'code': (BytesIO(code.encode('utf-8')), 'code.c')
        }
        source_url = post(f'/api/v1/tasks/{task_id}/results', payload, student_token, CONTENT_TYPE_FORM_DATA)[1]['source_url']
        return (source_url, student_token)

    def test_post_result_without_code_should_fail(self) -> None:
        task_id, student_token = self.__set_up_task_id_student_token()
        payload = {
            'file': (BytesIO(b'Random file.'), 'code.c')
        }
        response = post(f'/api/v1/tasks/{task_id}/results', payload, student_token, CONTENT_TYPE_FORM_DATA)

        assert response[0] == 400

    def test_post_result_without_filename_should_fail(self) -> None:
        task_id, student_token = self.__set_up_task_id_student_token()
        payload = {
            'code': (BytesIO(VALID_C_CODE.encode('utf-8')))
        }
        response = post(f'/api/v1/tasks/{task_id}/results', payload, student_token, CONTENT_TYPE_FORM_DATA)

        assert response[0] == 400

    def test_post_result_with_empty_filename_should_return_unprocessable_entity(self) -> None:
        task_id, student_token = self.__set_up_task_id_student_token()
        payload = {
            'code': (BytesIO(VALID_C_CODE.encode('utf-8')), '')
        }
        response = post(f'/api/v1/tasks/{task_id}/results', payload, student_token, CONTENT_TYPE_FORM_DATA)

        assert response[0] == 422

    def test_post_result_with_invalid_extension_should_return_unprocessable_entity(self) -> None:
        task_id, student_token = self.__set_up_task_id_student_token()
        payload = {
            'code': (BytesIO(VALID_C_CODE.encode('utf-8')), 'code.png')
        }
        response = post(f'/api/v1/tasks/{task_id}/results', payload, student_token, CONTENT_TYPE_FORM_DATA)

        assert response[0] == 422

    def test_post_result_with_invalid_file_size_should_return_invalid_file_size(self) -> None:
        filepath = get_filepath_of_size(round(1.1 * 1024 * 1024), extension='.c') # 1.1 MB
        task_id, student_token = self.__set_up_task_id_student_token()

        with open(filepath, 'rb') as file:
            payload = {
            'code': (file, 'code.c')
            }
            response = post(f'/api/v1/tasks/{task_id}/results', payload, student_token, CONTENT_TYPE_FORM_DATA)

            assert response[0] == 413

    def test_post_result_with_closed_group_should_return_forbidden(self) -> None:
        manager_token = get_manager_id_token()[1]
        student_token = get_student_id_token()[1]
        group_id = create_join_request_group_id(student_token, manager_token, approve=True)
        task_id = create_task_json(manager_token, group_id)['id']
        create_test_case_json(manager_token, task_id)
        update_payload = {
            'active': False
        }
        patch(f'api/v1/groups/{group_id}', update_payload, manager_token)

        payload = {
            'code': (BytesIO(VALID_C_CODE.encode('utf-8')), 'code.c')
        }
        response = post(f'/api/v1/tasks/{task_id}/results', payload, student_token, CONTENT_TYPE_FORM_DATA)

        assert response[0] == 403

    def test_post_result_with_not_started_task_should_return_forbidden(self) -> None:
        task_id, student_token = self.__set_up_task_id_student_token(starts_on=(datetime.now().astimezone() + timedelta(days=1)).isoformat())
        payload = {
            'code': (BytesIO(VALID_C_CODE.encode('utf-8')), 'code.c')
        }
        response = post(f'/api/v1/tasks/{task_id}/results', payload, student_token, CONTENT_TYPE_FORM_DATA)

        assert response[0] == 403

    def test_post_result_with_finished_task_should_return_forbidden(self) -> None:
        task_id, student_token = self.__set_up_task_id_student_token(starts_on=(datetime.now().astimezone() - timedelta(days=2)).isoformat(), ends_on=(datetime.now().astimezone() - timedelta(days=1)).isoformat())
        payload = {
            'code': (BytesIO(VALID_C_CODE.encode('utf-8')), 'code.c')
        }
        response = post(f'/api/v1/tasks/{task_id}/results', payload, student_token, CONTENT_TYPE_FORM_DATA)

        assert response[0] == 403

    def test_post_result_more_than_max_attempt_times_should_return_forbidden(self) -> None:
        task_id, student_token = self.__set_up_task_id_student_token(max_attempts=1)
        payload = {
            'code': (BytesIO(VALID_C_CODE.encode('utf-8')), 'code.c')
        }
        payload_second = {
            'code': (BytesIO(VALID_C_CODE.encode('utf-8')), 'code.c')
        }
        response_first = post(f'/api/v1/tasks/{task_id}/results', payload, student_token, CONTENT_TYPE_FORM_DATA)
        response_second = post(f'/api/v1/tasks/{task_id}/results', payload_second, student_token, CONTENT_TYPE_FORM_DATA)

        assert response_first[0] == 201
        assert response_first[1]['attempt_number'] == 1
        assert response_second[0] == 403

    def test_post_result_with_student_not_member_should_return_forbidden(self) -> None:
        manager_token = get_manager_id_token()[1]
        student_token = get_student_id_token()[1]
        group_id = create_join_request_group_id(student_token, manager_token, approve=False)
        task_id = create_task_json(manager_token, group_id)['id']
        create_test_case_json(manager_token, task_id)
        payload = {
            'code': (BytesIO(VALID_C_CODE.encode('utf-8')), 'code.c')
        }
        response = post(f'/api/v1/tasks/{task_id}/results', payload, student_token, CONTENT_TYPE_FORM_DATA)

        assert response[0] == 403

    def test_post_result_with_task_without_tests_should_return_forbidden(self) -> None:
        manager_token = get_manager_id_token()[1]
        student_token = get_student_id_token()[1]
        group_id = create_join_request_group_id(student_token, manager_token, approve=True)
        task_id = create_task_json(manager_token, group_id)['id']

        payload = {
            'code': (BytesIO(VALID_C_CODE.encode('utf-8')), 'code.c')
        }
        response = post(f'/api/v1/tasks/{task_id}/results', payload, student_token, CONTENT_TYPE_FORM_DATA)

        assert response[0] == 403

    def test_post_result_with_manager_should_return_unauthorized(self) -> None:
        manager_token = get_manager_id_token()[1]
        group_id = get_new_group_id_code(get_random_name(), manager_token)[0]
        task_id = create_task_json(manager_token, group_id)['id']
        create_test_case_json(manager_token, task_id)
        payload = {
            'code': (BytesIO(VALID_C_CODE.encode('utf-8')), 'code.c')
        }
        response = post(f'/api/v1/tasks/{task_id}/results', payload, manager_token, CONTENT_TYPE_FORM_DATA)

        assert response[0] == 401

    def test_post_result_with_invalid_task_id_should_return_not_found(self) -> None:
        student_token = get_student_id_token()[1]
        payload = {
            'code': (BytesIO(VALID_C_CODE.encode('utf-8')), 'code.c')
        }
        response = post(f'/api/v1/tasks/{999999}/results', payload, student_token, CONTENT_TYPE_FORM_DATA)

        assert response[0] == 404

    def test_post_result_with_invalid_c_code_should_succeed_and_fail_all_tests_with_same_message(self) -> None:
        task_id, student_token = self.__set_up_valid_2_open_2_closed_tests_task_id_student_token()
        payload = {
            'code': (BytesIO(INVALID_C_CODE.encode('utf-8')), 'code.c')
        }
        response = post(f'/api/v1/tasks/{task_id}/results', payload, student_token, CONTENT_TYPE_FORM_DATA)

        assert response[0] == 201
        result = response[1]
        assert result['attempt_number'] == 1
        assert result['correct_open'] == 0
        assert result['correct_closed'] == 0
        assert result['source_url'] == f'/api/v1/tasks/{task_id}/results/latest/code'
        open_results = result['open_results']
        assert len(open_results) == 2
        assert all(result['success'] is False for result in open_results)
        closed_results = result['closed_results']
        assert open_results[0]['diff'] == open_results[1]['diff'] # should be the same compilation error
        assert len(closed_results) == 2
        assert all(result['success'] is False for result in closed_results)
        assert all(result.get('diff') is None for result in closed_results)

    def test_post_result_with_valid_c_code_should_succeed_and_succeed_all_tests(self) -> None:
        task_id, student_token = self.__set_up_valid_2_open_2_closed_tests_task_id_student_token()
        payload = {
            'code': (BytesIO(VALID_C_CODE.encode('utf-8')), 'code.c')
        }
        response = post(f'/api/v1/tasks/{task_id}/results', payload, student_token, CONTENT_TYPE_FORM_DATA)

        assert response[0] == 201
        result = response[1]
        assert result['attempt_number'] == 1
        assert result['correct_open'] == 2
        assert result['correct_closed'] == 2
        assert result['source_url'] == f'/api/v1/tasks/{task_id}/results/latest/code'
        open_results = result['open_results']
        assert len(open_results) == 2
        assert all(result['success'] is True for result in open_results)
        closed_results = result['closed_results']
        assert all(result.get('diff') is None for result in open_results)
        assert len(closed_results) == 2
        assert all(result['success'] is True for result in closed_results)
        assert all(result.get('diff') is None for result in closed_results)

    def test_post_result_with_timeout_should_succeed_and_fail_tests_with_timeout(self) -> None:
        task_id, student_token = self.__set_up_task_id_student_token()
        payload = {
            'code': (BytesIO(TIMEOUT_C_CODE.encode('utf-8')), 'code.c')
        }
        response = post(f'/api/v1/tasks/{task_id}/results', payload, student_token, CONTENT_TYPE_FORM_DATA)

        assert response[0] == 201
        result = response[1]
        assert result['attempt_number'] == 1
        assert result['correct_open'] == 0
        assert result.get('correct_closed') is None
        assert result['source_url'] == f'/api/v1/tasks/{task_id}/results/latest/code'
        open_results = result['open_results']
        assert len(open_results) == 1
        open_result = open_results[0]
        assert open_result['success'] is False
        assert open_result['diff'] == 'Timeout.'
        closed_results = result['closed_results']
        assert len(closed_results) == 0

    def test_post_result_with_execution_error_should_succeed_and_fail_test_with_error(self) -> None:
        task_id, student_token = self.__set_up_task_id_student_token()
        payload = {
            'code': (BytesIO(RUNTIME_ERROR_C_CODE.encode('utf-8')), 'code.c')
        }
        response = post(f'/api/v1/tasks/{task_id}/results', payload, student_token, CONTENT_TYPE_FORM_DATA)

        assert response[0] == 201
        result = response[1]
        assert result['attempt_number'] == 1
        assert result['correct_open'] == 0
        assert result.get('correct_closed') is None
        assert result['source_url'] == f'/api/v1/tasks/{task_id}/results/latest/code'
        open_results = result['open_results']
        assert len(open_results) == 1
        open_result = open_results[0]
        assert open_result['success'] is False
        print(open_result['diff'])
        assert open_result['diff'] == 'Execution error:\nError'
        closed_results = result['closed_results']
        assert len(closed_results) == 0

    def test_download_latest_source_code_with_student_should_succeed(self) -> None:
        source_url, student_token = self.__set_up_result_source_code_url_student_token(VALID_C_CODE)

        response = get(source_url, student_token, decode_as_json=False)

        assert response[0] == 200
        assert str(response[1]) == VALID_C_CODE

    @pytest.mark.smoke
    def test_download_latest_source_code_with_multiple_results_should_return_latest(self) -> None:
        task_id, student_token = self.__set_up_task_id_student_token()
        payload_first = {
            'code': (BytesIO(VALID_C_CODE.encode('utf-8')), 'code.c')
        }
        source_url = post(f'/api/v1/tasks/{task_id}/results', payload_first, student_token, CONTENT_TYPE_FORM_DATA)[1]['source_url']
        payload_second = {
            'code': (BytesIO(INVALID_C_CODE.encode('utf-8')), 'code.c')
        }
        post(f'/api/v1/tasks/{task_id}/results', payload_second, student_token, CONTENT_TYPE_FORM_DATA)

        response = get(source_url, student_token, decode_as_json=False)

        assert response[0] == 200
        assert str(response[1]) == INVALID_C_CODE

    def test_download_latest_source_code_with_manager_should_return_unauthorized(self) -> None:
        manager_token = get_manager_id_token()[1]
        source_url = self.__set_up_result_source_code_url_student_token(VALID_C_CODE)[0]

        response = get(source_url, manager_token, decode_as_json=False)

        assert response[0] == 401

    def test_download_latest_source_code_with_another_student_should_return_forbidden(self) -> None:
        source_url = self.__set_up_result_source_code_url_student_token(VALID_C_CODE)[0]
        name = get_random_name()
        student_payload = {
            'name': name,
            'email': name + '@mail.com',
            'password': name + 'password'
        }
        another_student_token = post('/api/v1/students', student_payload)[1]['token']

        response = get(source_url, another_student_token, decode_as_json=False)

        assert response[0] == 403

    def test_download_latest_source_code_with_invalid_task_id_should_return_not_found(self) -> None:
        student_token = get_student_id_token()[1]

        response = get(f'/api/v1/tasks/{999999}/results/latest/code', student_token)

        assert response[0] == 404

    @pytest.mark.smoke
    def test_download_latest_source_code_without_result_should_return_not_found(self) -> None:
        task_id, student_token = self.__set_up_task_id_student_token()

        response = get(f'api/v1/tasks/{task_id}/results/latest/code', student_token, decode_as_json=False)

        assert response[0] == 404

    @pytest.mark.smoke
    def test_get_latest_result_with_student_should_succeed_and_return_latest_result(self) -> None:
        task_id, student_token = self.__set_up_valid_2_open_2_closed_tests_task_id_student_token()

        payload_first = {
            'code': (BytesIO(VALID_C_CODE.encode('utf-8')), 'code.c')
        }
        response_first = post(f'/api/v1/tasks/{task_id}/results', payload_first, student_token, CONTENT_TYPE_FORM_DATA)
        assert response_first[0] == 201
        assert response_first[1]['attempt_number'] == 1
        assert response_first[1]['correct_open'] == 2
        assert response_first[1]['correct_closed'] == 2

        # fail second open test and first closed test
        code = '''
#include<stdio.h>
int main() {
    int a, b;
    scanf("%d %d", &a, &b);
    if(a == 3 || a == 5) {
        return 0;
    }
    printf("%d", a+b);
}
'''
        payload_second = {
            'code': (BytesIO(code.encode('utf-8')), 'code.c')
        }
        response_second = post(f'/api/v1/tasks/{task_id}/results', payload_second, student_token, CONTENT_TYPE_FORM_DATA)
        assert response_second[0] == 201
        assert response_second[1]['attempt_number'] == 2
        assert response_second[1]['correct_open'] == 1
        assert response_second[1]['correct_closed'] == 1
        assert len(response_second[1]['open_results']) == 2
        assert len(response_second[1]['closed_results']) == 2
        assert response_second[1]['open_results'][0]['success'] is True
        assert response_second[1]['open_results'][0].get('diff') is None
        assert response_second[1]['open_results'][1]['success'] is False
        assert response_second[1]['open_results'][1].get('diff') is not None
        assert response_second[1]['closed_results'][0]['success'] is False
        assert response_second[1]['closed_results'][0].get('diff') is None
        assert response_second[1]['closed_results'][1]['success'] is True
        assert response_second[1]['closed_results'][1].get('diff') is None

        response = get(f'api/v1/tasks/{task_id}/results/latest', student_token)
        assert response[0] == 200
        assert response[1] == response_second[1]

    def test_get_latest_result_with_manager_should_return_unauthorized(self) -> None:
        task_id = self.__set_up_task_id_student_token()[0]
        manager_token = get_manager_id_token()[1]

        response = get(f'api/v1/tasks/{task_id}/results/latest', manager_token)
        assert response[0] == 401

    def test_get_latest_result_with_another_student_should_return_forbidden(self) -> None:
        task_id = self.__set_up_task_id_student_token()[0]
        name = get_random_name()
        student_payload = {
            'name': name,
            'email': name + '@mail.com',
            'password': name + 'password'
        }
        another_student_token = post('/api/v1/students', student_payload)[1]['token']

        response = get(f'api/v1/tasks/{task_id}/results/latest', another_student_token)
        assert response[0] == 403

    def test_get_latest_result_with_invalid_task_id_should_return_not_found(self) -> None:
        student_token = self.__set_up_task_id_student_token()[1]

        response = get(f'api/v1/tasks/{999999}/results/latest', student_token)
        assert response[0] == 404

    def test_get_latest_result_without_result_should_return_not_found(self) -> None:
        task_id, student_token = self.__set_up_task_id_student_token()

        response = get(f'api/v1/tasks/{task_id}/results/latest', student_token)
        assert response[0] == 404
