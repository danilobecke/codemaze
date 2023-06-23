from tests.helper import post, get_random_name, assert_user_response

class TestManager:
    __name = get_random_name()
    __email = f'{__name}@email.com'
    __password = f'pass{__name}'

    def test_create_manager_should_create(self):
        payload = {
            'name': self.__name,
            'email': self.__email,
            'password': self.__password
        }
        response = post('/managers', payload)

        assert_user_response(response, self.__name, self.__email, 'manager')

    def test_login_should_work(self):
        payload = {
            'email': self.__email,
            'password': self.__password
        }
        response = post('/session', payload)

        assert_user_response(response, self.__name, self.__email, 'manager')

    def test_create_manager_missing_name_should_return_bad_request(self):
        payload = {
            'email': self.__email,
            'password': self.__password
        }
        response = post('/managers', payload)

        assert response[0] == 400

    def test_create_manager_missing_email_should_return_bad_request(self):
        payload = {
            'name': self.__name,
            'password': self.__password
        }
        response = post('/managers', payload)

        assert response[0] == 400

    def test_create_manager_missing_password_should_return_bad_request(self):
        payload = {
            'name': self.__name,
            'email': self.__email
        }
        response = post('/managers', payload)

        assert response[0] == 400

    def test_create_manager_same_email_should_return_server_error(self):
        payload = {
            'name': self.__name,
            'email': self.__email,
            'password': self.__password
        }
        response = post('/managers', payload)

        assert response[0] == 500

    def test_create_manager_with_invalid_email_should_return_bad_request(self):
        payload = {
            'name': get_random_name(),
            'email': 'invalid-email',
            'password': 'password'
        }
        response = post('/managers', payload)

        assert response[0] == 400
