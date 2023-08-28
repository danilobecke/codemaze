import pytest

from tests.helper import post, get_random_name, assert_user_response, get_user_payload

class TestManager:
    @pytest.mark.smoke
    def test_create_manager_should_create(self) -> None:
        payload = get_user_payload()
        response = post('/api/v1/managers', payload)

        assert_user_response(response, payload['name'], payload['email'], 'manager')

    @pytest.mark.smoke
    def test_login_should_work(self) -> None:
        user_payload = get_user_payload()
        post('/api/v1/managers', user_payload)

        payload = {
            'email': user_payload['email'],
            'password': user_payload['password']
        }
        response = post('/api/v1/session', payload)

        assert_user_response(response, user_payload['name'], user_payload['email'], 'manager', 200)

    def test_create_manager_missing_name_should_return_bad_request(self) -> None:
        payload = {
            'email': get_random_name() + '@mail.com',
            'password': 'password'
        }
        response = post('/api/v1/managers', payload)

        assert response[0] == 400

    def test_create_manager_missing_email_should_return_bad_request(self) -> None:
        payload = {
            'name': get_random_name(),
            'password': 'password'
        }
        response = post('/api/v1/managers', payload)

        assert response[0] == 400

    def test_create_manager_missing_password_should_return_bad_request(self) -> None:
        name = get_random_name()
        payload = {
            'name': name,
            'email': name + '@mail.com'
        }
        response = post('/api/v1/managers', payload)

        assert response[0] == 400

    def test_create_manager_same_email_should_return_conflict(self) -> None:
        payload = get_user_payload()

        response_one = post('/api/v1/managers', payload.copy())
        response_two = post('/api/v1/managers', payload)

        assert response_one[0] == 201
        assert response_two[0] == 409

    def test_create_manager_with_invalid_email_should_return_bad_request(self) -> None:
        payload = {
            'name': get_random_name(),
            'email': 'invalid-email',
            'password': 'password'
        }
        response = post('/api/v1/managers', payload)

        assert response[0] == 400
