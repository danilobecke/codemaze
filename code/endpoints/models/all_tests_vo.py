from endpoints.models.tcase_vo import TCaseVO

class AllTestsVO:
    def __init__(self, open_tests: list[TCaseVO], closed_tests: list[TCaseVO]) -> None:
        self.open_tests = open_tests
        self.closed_tests = closed_tests
