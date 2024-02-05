import pytest

from tests.helper import post, patch, get_random_name, assert_user_response, get_user_payload

class TestUser:
    @pytest.mark.smoke
    def test_update_manager_name_should_work(self) -> None:
        self.__patch_user_name('manager')

    def __patch_user_name(self, role: str = 'manager', payload: dict[str, str] | None = None, updated_name: str | None = None) -> None:
        user_payload = payload if payload else get_user_payload()
        endpoint = 'managers' if role == 'manager' else 'students'
        token = post(f'/api/v1/{endpoint}', user_payload)[1]['token']

        payload = {
            'name': updated_name if updated_name else get_random_name(),
        }
        response = patch('/api/v1/user', payload, token)

        assert_user_response(response, payload['name'], user_payload['email'], role, False, 200)

    @pytest.mark.smoke
    def test_update_student_name_should_work(self) -> None:
        self.__patch_user_name('student')

    def test_update_name_with_same_name_should_work(self) -> None:
        user_payload = get_user_payload()
        self.__patch_user_name(payload=user_payload, updated_name=user_payload['name'])

    def test_update_user_wit_empty_body_should_work_and_not_update(self) -> None:
        user_payload = get_user_payload()
        token = post('/api/v1/managers', user_payload)[1]['token']

        response = patch('/api/v1/user', {}, token)

        assert_user_response(response, user_payload['name'], user_payload['email'], 'manager', False, 200)

    def test_update_user_without_token_should_return_unauthorized(self) -> None:
        response = patch('/api/v1/user', {}, 'invalid-token')

        assert response[0] == 401

    @pytest.mark.smoke
    def test_update_user_password_should_work(self) -> None:
        user_payload = get_user_payload()
        token = post('/api/v1/managers', user_payload)[1]['token']

        new_password = get_random_name()
        payload = {
            'password': {
                'current': user_payload['password'],
                'new': new_password
            }
        }
        response = patch('/api/v1/user', payload, token)
        assert response[0] == 200

        login_payload = {
            'email': user_payload['email'],
            'password': new_password
        }
        login_response = post('/api/v1/session', login_payload)
        assert_user_response(login_response, user_payload['name'], user_payload['email'], 'manager', status_code=200)

        login_payload['password'] = user_payload['password']
        login_response = post('/api/v1/session', login_payload)
        assert login_response[0] == 403

    def test_update_user_password_with_wrong_current_password_should_return_unprocessable_entity(self) -> None:
        user_payload = get_user_payload()
        token = post('/api/v1/students', user_payload)[1]['token']

        payload = {
            'password': {
                'current': 'wrong-password',
                'new': get_random_name()
            }
        }
        response = patch('/api/v1/user', payload, token)
        assert response[0] == 422

    def test_update_user_password_without_required_field_should_return_bad_request(self) -> None:
        user_payload = get_user_payload()
        token = post('/api/v1/managers', user_payload)[1]['token']

        payload = {
            'password': {
                'new': get_random_name()
            }
        }
        response = patch('/api/v1/user', payload, token)
        assert response[0] == 400

        payload = {
            'password': {
                'current': user_payload['password']
            }
        }
        response = patch('/api/v1/user', payload, token)
        assert response[0] == 400
