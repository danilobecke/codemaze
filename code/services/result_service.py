from collections import Counter
from datetime import datetime
from functools import reduce
from itertools import groupby
from threading import Thread
from typing import Callable, Optional

from endpoints.models.all_tests_vo import AllTestsVO
from endpoints.models.group import GroupVO
from endpoints.models.report_vo import ReportVO, StudentReport, OverallReport, ResultPercentage, TestReport
from endpoints.models.result_vo import ResultVO
from endpoints.models.task_vo import TaskVO
from endpoints.models.tcase_result_vo import TCaseResultVO
from endpoints.models.user import UserVO
from helpers.commons import file_extension, source_code_download_url
from helpers.exceptions import Forbidden
from helpers.file import File
from helpers.role import Role
from helpers.unwrapper import unwrap
from repository.result_repository import ResultRepository
from repository.dto.result import ResultDTO
from services.runner_service import RunnerService
from services.moss_service import MossService

class ResultService:
    def __init__(self, runner_service: RunnerService, moss_service: Optional[MossService]) -> None:
        self.__runner_service = runner_service
        self.__moss_service = moss_service
        self.__result_repository = ResultRepository()

    def run(self, user: UserVO, task: TaskVO, tests: AllTestsVO, file: File) -> ResultVO:
        now = datetime.now().astimezone()
        if (len(tests.closed_tests) + len(tests.open_tests)) < 1:
            raise Forbidden() # Prevent running without tests
        if unwrap(task.starts_on) > now or (task.ends_on is not None and task.ends_on < now):
            raise Forbidden()
        attempt_number = self.__result_repository.get_number_of_results(user.id, task.id) + 1
        if task.max_attempts is not None and attempt_number > task.max_attempts:
            raise Forbidden()
        file_path = file.save(self.__runner_service.allowed_extensions(task.languages))
        dto = ResultDTO()
        dto.correct_open = 0
        dto.correct_closed = 0
        dto.file_path = file_path
        dto.student_id = user.id
        dto.task_id = task.id
        stored = self.__result_repository.add(dto)
        results = self.__runner_service.run(file_path, tests, stored.id)
        open_results = list(filter(lambda result: any(result.test_case_id == test.id for test in tests.open_tests) , results))
        closed_results = list(filter(lambda result: any(result.test_case_id == test.id for test in tests.closed_tests) , results))
        reducer: Callable[[int, TCaseResultVO], int] = lambda current, result: current + (1 if result.success else 0)
        stored.correct_open = reduce(reducer, open_results, 0)
        stored.correct_closed = reduce(reducer, closed_results, 0)
        self.__result_repository.update_session()
        for result in closed_results:
            result.diff = None
        return ResultVO.import_from_dto(stored, attempt_number, open_results, closed_results)

    def get_latest_source_code_name_path(self, task: TaskVO, user_id: int) -> tuple[str, str]:
        dto = self.__result_repository.get_latest_result(user_id, task.id)
        path = dto.file_path
        return ('source' + file_extension(path), path)

    def get_latest_result(self, task: TaskVO, user: UserVO, tests: AllTestsVO) -> ResultVO:
        dto = self.__result_repository.get_latest_result(user.id, task.id)
        number_off_attempts = self.__result_repository.get_number_of_results(user.id, task.id)
        test_results = self.__runner_service.get_test_results(dto.id)
        open_results = list(filter(lambda result: any(result.test_case_id == test.id for test in tests.open_tests) , test_results))
        closed_results = list(filter(lambda result: any(result.test_case_id == test.id for test in tests.closed_tests) , test_results))
        if user.role == Role.STUDENT:
            for result in closed_results:
                result.diff = None
        return ResultVO.import_from_dto(dto, number_off_attempts, open_results, closed_results)

    def get_source_code_from_result_name_path(self, result_id: int, user_id: int, user_groups: list[GroupVO], get_task_func: Callable[[int, int, list[GroupVO]], TaskVO]) -> tuple[str, str]:
        dto = self.__result_repository.find(result_id)
        get_task_func(dto.task_id, user_id, user_groups) # assert has access to the task -> is manager
        path = dto.file_path
        return ('source' + file_extension(path), path)

    def __get_students_report(self, task_results: list[ResultDTO], students: list[UserVO], tests: AllTestsVO) -> list[StudentReport]:
        number_open_tests = len(tests.open_tests)
        number_closed_tests = len(tests.closed_tests)
        student_reports = [ StudentReport(student.id, student.name) for student in students ]
        for report in student_reports:
            results = [ result for result in task_results if result.student_id == report.id ]
            try:
                valid_result = results[-1] # last submitted
                report.open_result_percentage = round((valid_result.correct_open / number_open_tests) * 100, 2)
                report.closed_result_percentage = round((valid_result.correct_closed / number_closed_tests) * 100, 2) if number_closed_tests > 0 else None
                report.result_percentage = round((report.open_result_percentage + report.closed_result_percentage) / 2, 2) if report.closed_result_percentage else report.open_result_percentage
                report.number_attempts = len(results)
                report.source_code_url = source_code_download_url(valid_result.id)
                wrong_tests: list[int] = []
                if report.result_percentage != 100:
                    wrong_tests = [ tcase_result.test_case_id for tcase_result in [ tc_result for tc_result in self.__runner_service.get_test_results(valid_result.id) if tc_result.diff is not None ] ]
                report.wrong_tests_id = wrong_tests
            except IndexError:
                # student didn't submit any result
                report.open_result_percentage = 0
                report.closed_result_percentage = 0 if number_closed_tests > 0 else None
                report.result_percentage = 0
                report.number_attempts = 0
                report.source_code_url = None
                report.wrong_tests_id = []
        return student_reports

    def __get_overall_report(self, students_report: list[StudentReport]) -> OverallReport:
        number_of_students = len(students_report)
        submissions_percentage = 0 if number_of_students == 0 else round((len([report for report in students_report if report.number_attempts > 0]) / number_of_students) * 100, 2)
        mean_attempts_success: int | None = None
        results_percentage: list[ResultPercentage] = []
        for result, reports in groupby(students_report, lambda report: report.result_percentage):
            reports_list = list(reports)
            number_of_reports = len(reports_list)
            results_percentage.append(ResultPercentage(result, round((number_of_reports / number_of_students) * 100, 2)))
            if result == 100:
                mean_attempts_success = int(round(reduce(lambda current, report: current + report.number_attempts, reports_list, 0) / number_of_reports, 0))
        all_wrong_tests: list[int] = []
        for report in students_report:
            all_wrong_tests.extend(report.wrong_tests_id)
        most_common = Counter(all_wrong_tests).most_common()
        tests_more_failures = []
        if len(most_common) > 0:
            most_common_count = most_common[0][1]
            tests_more_failures = [ x[0] for x in most_common if x[1] == most_common_count ]
        return OverallReport(submissions_percentage, sorted(results_percentage, reverse=True), mean_attempts_success, None, tests_more_failures)

    def __get_tests_report(self, students_report: list[StudentReport], tests: AllTestsVO) -> list[TestReport]:
        students_with_results = [ report for report in students_report if report.number_attempts > 0 ]
        number_of_submissions = len(students_with_results)
        reports: list[TestReport] = []
        for test in tests.open_tests + tests.closed_tests:
            correct_percentage: float = 0
            if number_of_submissions > 0:
                correct_percentage = round((1 - (len([ report for report in students_with_results if test.id in report.wrong_tests_id ]) / number_of_submissions)) * 100, 2)
            reports.append(TestReport(test.id, correct_percentage))
        return reports

    def __get_moss_report(self, languages: list[str], task_results: list[ResultDTO], students: list[UserVO], urls: list[str]) -> None:
        if self.__moss_service is None:
            return
        if len(languages) > 1:
            # TODO LOGGER
            return
        task_results.reverse() # the latest is the relevant one
        results: list[ResultDTO] = []
        for result in task_results:
            if result.student_id not in [ _result.student_id for _result in results ]:
                results.append(result)
        filepath_name_list: list[tuple[str, str]] = []
        for result in results:
            try:
                student_name = next(student.name for student in students if student.id == result.student_id)
                filepath_name_list.append((result.file_path, student_name))
            except StopIteration:
                continue
        self.__moss_service.get_report(filepath_name_list, languages[0], urls)
        return

    def get_results_report(self, task: TaskVO, students: list[UserVO], tests: AllTestsVO) -> ReportVO:
        task_results = self.__result_repository.get_results_for_task(task.id)
        moss_urls: list[str] = []
        thread = Thread(target=self.__get_moss_report, args=[task.languages, task_results.copy(), students, moss_urls])
        thread.start()
        students_report = self.__get_students_report(task_results, students, tests)
        overall_report = self.__get_overall_report(students_report)
        tests_report = self.__get_tests_report(students_report, tests)
        thread.join()
        report_url = moss_urls[0] if len(moss_urls) > 0 else None
        overall_report.plagiarism_report_url = report_url
        # TODO store URL on task
        return ReportVO(overall_report, students_report, tests_report)
