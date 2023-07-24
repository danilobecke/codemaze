from tests.helper import post, get_random_name, assert_user_response

class TestStudent:
    __name = get_random_name()
    __email = f'{__name}@email.com'
    __password = f'pass{__name}'

    def test_create_student_should_create(self):
        payload = {
            'name': self.__name,
            'email': self.__email,
            'password': self.__password
        }
        response = post('/students', payload)

        assert_user_response(response, self.__name, self.__email, 'student')

    def test_login_should_work(self):
        payload = {
            'email': self.__email,
            'password': self.__password
        }
        response = post('/session', payload)

        assert_user_response(response, self.__name, self.__email, 'student', 200)

    def test_login_missing_email_should_return_bad_request(self):
        payload = {
            'password': self.__password
        }
        response = post('/session', payload)

        assert response[0] == 400

    def test_login_missing_password_should_return_bad_request(self):
        payload = {
            'email': self.__email
        }
        response = post('/session', payload)

        assert response[0] == 400

    def test_login_wrong_email_should_return_forbidden(self):
        payload = {
            'email': 'some-random-email@email.com',
            'password': self.__password
        }
        response = post('/session', payload)

        assert response[0] == 403

    def test_login_wrong_password_should_return_forbidden(self):
        payload = {
            'email': self.__email,
            'password': 'some-random-password'
        }
        response = post('/session', payload)

        assert response[0] == 403

    def test_create_student_same_email_should_return_server_error(self):
        payload = {
            'name': self.__name,
            'email': self.__email,
            'password': self.__password
        }
        response = post('/students', payload)

        assert response[0] == 500

    def test_login_with_invalid_email_should_return_bad_request(self):
        payload = {
            'email': 'invalid-email',
            'password': 'password'
        }
        response = post('/session', payload)

        assert response[0] == 400

    def test_create_user_with_invalid_email_should_return_bad_request(self):
        payload = {
            'name': get_random_name(),
            'email': 'invalid-email',
            'password': 'password'
        }
        response = post('/students', payload)

        assert response[0] == 400
