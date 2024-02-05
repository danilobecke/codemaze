import pytest

from tests.helper import post, get_random_name, assert_user_response, get_user_payload

class TestStudent:
    @pytest.mark.smoke
    def test_create_student_should_create(self) -> None:
        payload = get_user_payload()
        response = post('/api/v1/students', payload)

        assert_user_response(response, payload['name'], payload['email'], 'student')

    @pytest.mark.smoke
    def test_login_should_work(self) -> None:
        user_payload = get_user_payload()
        post('/api/v1/students', user_payload)

        payload = {
            'email': user_payload['email'],
            'password': user_payload['password']
        }
        response = post('/api/v1/session', payload)

        assert_user_response(response, user_payload['name'], user_payload['email'], 'student', status_code=200)

    def test_login_missing_email_should_return_bad_request(self) -> None:
        payload = {
            'password': 'password'
        }
        response = post('/api/v1/session', payload)

        assert response[0] == 400

    def test_login_missing_password_should_return_bad_request(self) -> None:
        payload = {
            'email': 'mail@mail.com'
        }
        response = post('/api/v1/session', payload)

        assert response[0] == 400

    def test_login_wrong_email_should_return_forbidden(self) -> None:
        user_payload = get_user_payload()
        post('/api/v1/students', user_payload)

        payload = {
            'email': get_random_name() + '@mail.com',
            'password': user_payload['password']
        }
        response = post('/api/v1/session', payload)

        assert response[0] == 403

    @pytest.mark.smoke
    def test_login_wrong_password_should_return_forbidden(self) -> None:
        user_payload = get_user_payload()
        post('/api/v1/students', user_payload)

        payload = {
            'email': user_payload['email'],
            'password': get_random_name()
        }
        response = post('/api/v1/session', payload)

        assert response[0] == 403

    def test_create_student_same_email_should_return_conflict(self) -> None:
        payload = get_user_payload()

        response_one = post('/api/v1/students', payload.copy())
        response_two = post('/api/v1/students', payload)

        assert response_one[0] == 201
        assert response_two[0] == 409

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
