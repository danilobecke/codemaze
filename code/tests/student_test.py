from tests.helper import post, get_random_name, assert_user_response

class TestStudent:
    __name = get_random_name()
    __email = f'{__name}@email.com'
    __password = f'pass{__name}'

    def test_create_student_should_create(self) -> None:
        payload = {
            'name': self.__name,
            'email': self.__email,
            'password': self.__password
        }
        response = post('/api/v1/students', payload)

        assert_user_response(response, self.__name, self.__email, 'student')

    def test_login_should_work(self) -> None:
        payload = {
            'email': self.__email,
            'password': self.__password
        }
        response = post('/api/v1/session', payload)

        assert_user_response(response, self.__name, self.__email, 'student', 200)

    def test_login_missing_email_should_return_bad_request(self) -> None:
        payload = {
            'password': self.__password
        }
        response = post('/api/v1/session', payload)

        assert response[0] == 400

    def test_login_missing_password_should_return_bad_request(self) -> None:
        payload = {
            'email': self.__email
        }
        response = post('/api/v1/session', payload)

        assert response[0] == 400

    def test_login_wrong_email_should_return_forbidden(self) -> None:
        payload = {
            'email': 'some-random-email@email.com',
            'password': self.__password
        }
        response = post('/api/v1/session', payload)

        assert response[0] == 403

    def test_login_wrong_password_should_return_forbidden(self) -> None:
        payload = {
            'email': self.__email,
            'password': 'some-random-password'
        }
        response = post('/api/v1/session', payload)

        assert response[0] == 403

    def test_create_student_same_email_should_return_server_error(self) -> None:
        payload = {
            'name': self.__name,
            'email': self.__email,
            'password': self.__password
        }
        response = post('/api/v1/students', payload)

        assert response[0] == 500

    def test_login_with_invalid_email_should_return_bad_request(self) -> None:
        payload = {
            'email': 'invalid-email',
            'password': 'password'
        }
        response = post('/api/v1/session', payload)

        assert response[0] == 400

    def test_create_user_with_invalid_email_should_return_bad_request(self) -> None:
        payload = {
            'name': get_random_name(),
            'email': 'invalid-email',
            'password': 'password'
        }
        response = post('/api/v1/students', payload)

        assert response[0] == 400
