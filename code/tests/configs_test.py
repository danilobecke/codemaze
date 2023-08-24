from tests.helper import get

import pytest

class TestConfigs:
    @pytest.mark.smoke
    def test_get_configs_should_succeed(self) -> None:
        response = get('/api/v1/configs')
        assert response[0] == 200
        assert len(response[1]['configs']) > 0
