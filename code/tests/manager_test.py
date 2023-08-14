import pytest

from tests.helper import post, get_random_name, assert_user_response

class TestManager:
    __name = get_random_name()
    __email = f'{__name}@email.com'
    __password = f'pass{__name}'

    @pytest.mark.smoke
    def test_create_manager_should_create(self) -> None:
        payload = {
            'name': self.__name,
            'email': self.__email,
            'password': self.__password
        }
        response = post('/api/v1/managers', payload)

        assert_user_response(response, self.__name, self.__email, 'manager')

    @pytest.mark.smoke
    def test_login_should_work(self) -> None:
        payload = {
            'email': self.__email,
            'password': self.__password
        }
        response = post('/api/v1/session', payload)

        assert_user_response(response, self.__name, self.__email, 'manager', 200)

    def test_create_manager_missing_name_should_return_bad_request(self) -> None:
        payload = {
            'email': self.__email,
            'password': self.__password
        }
        response = post('/api/v1/managers', payload)

        assert response[0] == 400

    def test_create_manager_missing_email_should_return_bad_request(self) -> None:
        payload = {
            'name': self.__name,
            'password': self.__password
        }
        response = post('/api/v1/managers', payload)

        assert response[0] == 400

    def test_create_manager_missing_password_should_return_bad_request(self) -> None:
        payload = {
            'name': self.__name,
            'email': self.__email
        }
        response = post('/api/v1/managers', payload)

        assert response[0] == 400

    def test_create_manager_same_email_should_return_server_error(self) -> None:
        payload = {
            'name': self.__name,
            'email': self.__email,
            'password': self.__password
        }
        response = post('/api/v1/managers', payload)

        assert response[0] == 500

    def test_create_manager_with_invalid_email_should_return_bad_request(self) -> None:
        payload = {
            'name': get_random_name(),
            'email': 'invalid-email',
            'password': 'password'
        }
        response = post('/api/v1/managers', payload)

        assert response[0] == 400
