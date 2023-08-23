from __future__ import annotations
from functools import total_ordering

class ReportVO:
    def __init__(self, overall: OverallReport, students: list[StudentReport], tests: list[TestReport]) -> None:
        self.overall = overall
        self.students = students
        self.tests = tests

class StudentReport:
    def __init__(self, id: int, name: str) -> None:
        self.id = id
        self.name = name
        self.open_result_percentage: float = -1
        self.closed_result_percentage: float | None = None
        self.result_percentage: float = -1
        self.number_attempts = -1
        self.source_code_url: str | None = None
        self.wrong_tests_id: list[int] = []

class OverallReport:
    def __init__(self, submissions_percentage: float, results_percentages: list[ResultPercentage], mean_attempts_success_all: int | None, tests_more_failures: list[int]) -> None:
        self.submissions_percentage = submissions_percentage
        self.results_percentages = results_percentages
        self.mean_attempts_success_all = mean_attempts_success_all
        self.plagiarism_report_urls: list[str] = []
        self.tests_more_failures = tests_more_failures

@total_ordering
class ResultPercentage:
    def __init__(self, result_percentage: float, students_percentage: float) -> None:
        self.result_percentage = result_percentage
        self.students_percentage = students_percentage

    def __lt__(self, obj: ResultPercentage) -> bool:
        return self.result_percentage < obj.result_percentage

class TestReport:
    def __init__(self, id: int, correct_percentage: float) -> None:
        self.id = id
        self.correct_percentage = correct_percentage
