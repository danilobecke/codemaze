from tests.helper import get, get_script_path

import pytest

class TestConfigs:
    @pytest.mark.smoke
    def test_get_configs_should_succeed(self) -> None:
        response = get('/api/v1/configs')
        assert response[0] == 200
        assert response[1]['create_test_script_url'] == '/api/v1/configs/create_test_script'
        assert len(response[1]['configs']) > 0

    @pytest.mark.smoke
    def test_download_create_test_script_should_succeed(self) -> None:
        response = get('/api/v1/configs/create_test_script', decode_as_json=False)
        assert response[0] == 200
        with open(get_script_path('create_test_case.py'), encoding='utf-8') as script:
            assert str(response[1]) == script.read()
