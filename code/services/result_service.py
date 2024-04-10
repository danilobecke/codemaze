from collections import Counter
from datetime import datetime, timedelta
from functools import reduce
from itertools import groupby
import os
from threading import Thread
from typing import Callable, Optional

from endpoints.models.all_tests_vo import AllTestsVO
from endpoints.models.group import GroupVO
from endpoints.models.report_vo import ReportVO, StudentReport, OverallReport, ResultPercentage, TestReport
from endpoints.models.result_vo import ResultVO
from endpoints.models.task_vo import TaskVO
from endpoints.models.tcase_result_vo import TCaseResultVO
from endpoints.models.user import UserVO
from helpers.commons import file_extension, source_code_download_url, secure_filename, compute_percentage
from helpers.config import Config
from helpers.exceptions import Forbidden, ServerError
from helpers.file import File
from helpers.role import Role
from helpers.unwrapper import unwrap
from repository.plagiarism_report_repository import PlagiarismReportRepository
from repository.result_repository import ResultRepository
from repository.dto.plagiarism_report_dto import PlagiarismReportDTO
from repository.dto.result import ResultDTO
from services.runner_service import RunnerService
from services.moss_service import MossService

class ResultService:
    def __init__(self, runner_service: RunnerService, moss_service: Optional[MossService]) -> None:
        self.__runner_service = runner_service
        self.__moss_service = moss_service
        self.__result_repository = ResultRepository()
        self.__plagiarism_report_repository = PlagiarismReportRepository()

    def run(self, user: UserVO, task: TaskVO, tests: AllTestsVO, file: File) -> ResultVO:
        if (len(tests.closed_tests) + len(tests.open_tests)) < 1:
            raise Forbidden() # Prevent running without tests
        match user.role:
            case Role.STUDENT:
                return self.__run_as_student(user, task, tests, file)
            case Role.MANAGER:
                return self.__run_as_manager(user, task, tests, file)

    def __run_as_student(self, user: UserVO, task: TaskVO, tests: AllTestsVO, file: File) -> ResultVO:
        now = datetime.now().astimezone()
        if unwrap(task.starts_on) > now or (task.ends_on is not None and task.ends_on < now):
            raise Forbidden()
        attempt_number = self.__result_repository.get_number_of_results(user.id, task.id) + 1
        if task.max_attempts is not None and attempt_number > task.max_attempts:
            raise Forbidden()
        stored = self.__result_repository.add(self.__create_result_dto(user, task, file))
        try:
            results = self.__runner_service.run(stored.file_path, tests, stored.id, should_save=True)
            open_results, closed_results = self.__split_open_closed_results(results, tests)
            correct_open, correct_closed = self.__compute_correct_open_correct_closed(open_results, closed_results)
            stored.correct_open = correct_open
            stored.correct_closed = correct_closed
            self.__result_repository.update_session()
            for result in closed_results:
                result.diff = None
            return ResultVO.import_from_dto(stored, attempt_number, open_results, closed_results)
        except ServerError as e:
            # rollback
            os.remove(stored.file_path)
            self.__result_repository.delete(stored.id)
            raise e

    def __run_as_manager(self, user: UserVO, task: TaskVO, tests: AllTestsVO, file: File) -> ResultVO:
        dto = self.__create_result_dto(user, task, file)
        dto.id = -1
        try:
            results = self.__runner_service.run(dto.file_path, tests, dto.id, should_save=False)
            os.remove(dto.file_path)
            open_results, closed_results = self.__split_open_closed_results(results, tests)
            correct_open, correct_closed = self.__compute_correct_open_correct_closed(open_results, closed_results)
            dto.correct_open = correct_open
            dto.correct_closed = correct_closed
            return ResultVO.import_from_dto(dto, -1, open_results, closed_results)
        except ServerError as e:
            # rollback
            os.remove(dto.file_path)
            raise e

    def __create_result_dto(self, user: UserVO, task: TaskVO, file: File) -> ResultDTO:
        code_max_size_mb = float(Config.get('files.code-max-size-mb'))
        file_path = file.save(self.__runner_service.allowed_extensions(task.languages), max_file_size_mb=code_max_size_mb)
        dto = ResultDTO()
        dto.correct_open = 0
        dto.correct_closed = 0
        dto.file_path = file_path
        dto.student_id = user.id
        dto.task_id = task.id
        return dto

    def __split_open_closed_results(self, tcase_results: list[TCaseResultVO], tests: AllTestsVO) -> tuple[list[TCaseResultVO], list[TCaseResultVO]]:
        open_results = list(filter(lambda result: any(result.test_case_id == test.id for test in tests.open_tests) , tcase_results))
        closed_results = list(filter(lambda result: any(result.test_case_id == test.id for test in tests.closed_tests) , tcase_results))
        return (open_results, closed_results)

    def __compute_correct_open_correct_closed(self, open_results: list[TCaseResultVO], closed_results: list[TCaseResultVO]) -> tuple[int, int]:
        reducer: Callable[[int, TCaseResultVO], int] = lambda current, result: current + (1 if result.success else 0)
        return (reduce(reducer, open_results, 0), reduce(reducer, closed_results, 0))

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

    def get_source_code_from_result_name_path(self, result_id: int, user_id: int, user_groups: list[GroupVO], get_task_func: Callable[[int, int, list[GroupVO]], TaskVO], get_student_func: Callable[[int], UserVO]) -> tuple[str, str]:
        dto = self.__result_repository.find(result_id)
        get_task_func(dto.task_id, user_id, user_groups) # assert has access to the task -> is manager
        path = dto.file_path
        student = get_student_func(dto.student_id)
        filename = secure_filename('source_' + student.name + file_extension(path))
        return (filename, path)

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
                report.result_percentage = compute_percentage(report.open_result_percentage, report.closed_result_percentage, number_open_tests, number_closed_tests)
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
        # groupby requires a sorted list
        for result, reports in groupby(sorted(students_report), lambda report: report.result_percentage):
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
        return OverallReport(submissions_percentage, sorted(results_percentage, reverse=True), mean_attempts_success, tests_more_failures)

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

    # pylint: disable=too-many-branches
    def __get_plagiarism_report(self, task: TaskVO, task_results: list[ResultDTO], students: list[UserVO], urls: list[str]) -> None:
        if self.__moss_service is None or task.ends_on is None:
            return # MOSS user ID not set or task without ends_on set
        if task.ends_on >= datetime.now().astimezone():
            return # task didn't finish
        reports = self.__plagiarism_report_repository.get_reports_for_task(task.id)
        if len(reports) > 0:
            # assert they are valid (one week)
            if any(report.created_at + timedelta(days=7) < datetime.now().astimezone() for report in reports):
                # delete all and create again
                for report in reports:
                    self.__plagiarism_report_repository.delete(report.id)
            else:
                urls.extend([ report.url for report in reports ])
                return
        task_results.reverse() # the latest is the relevant one
        results: list[ResultDTO] = []
        for result in task_results:
            # keep only one result per student
            if result.student_id not in [ _result.student_id for _result in results ]:
                results.append(result)
        for extension, _results in groupby(results, lambda result: file_extension(result.file_path)):
            filepath_name_list: list[tuple[str, str]] = []
            language = self.__runner_service.language_with_extension(extension)
            if language is None:
                continue
            for result in _results:
                try:
                    student_name = next(student.name for student in students if student.id == result.student_id)
                    filepath_name_list.append((result.file_path, student_name))
                except StopIteration:
                    continue
            report_url = self.__moss_service.get_report(filepath_name_list, language)
            if report_url is None:
                continue
            dto = PlagiarismReportDTO()
            dto.language = language
            dto.url = report_url
            dto.task_id = task.id
            self.__plagiarism_report_repository.add(dto)
            urls.append(report_url)

    def get_results_report(self, task: TaskVO, students: list[UserVO], tests: AllTestsVO) -> ReportVO:
        task_results = self.__result_repository.get_results_for_task(task.id)
        plagiarism_report_urls: list[str] = []
        thread = Thread(target=self.__get_plagiarism_report, args=[task, task_results.copy(), students, plagiarism_report_urls])
        thread.start()
        students_report = self.__get_students_report(task_results, students, tests)
        overall_report = self.__get_overall_report(students_report)
        tests_report = self.__get_tests_report(students_report, tests)
        thread.join()
        overall_report.plagiarism_report_urls = plagiarism_report_urls
        return ReportVO(overall_report, students_report, tests_report)
