from tests.helper import post
import uuid

class TestStudent:
    __name = str(uuid.uuid1())
    __email = f'{__name}@email.com'
    __password = f'pass{__name}'

    def test_create_student_should_create(self):
        payload = {
            'name': self.__name,
            'email': self.__email,
            'password': self.__password
        }
        response = post('/students', payload)

        assert response[0] == 200
        json = response[1]
        assert json['id'] is not None
        assert json['name'] == self.__name
        assert json['email'] == self.__email
        assert json['role'] == 'student'
        assert json['token'] is not None

    def test_login_should_work(self):
        payload = {
            'email': self.__email,
            'password': self.__password
        }
        response = post('/session', payload)

        assert response[0] == 200
        json = response[1]
        assert json['id'] is not None
        assert json['name'] == self.__name
        assert json['email'] == self.__email
        assert json['role'] == 'student'
        assert json['token'] is not None
    
    def test_login_missing_email_should_fail(self):
        payload = {
            'password': self.__password
        }
        response = post('/session', payload)

        assert response[0] == 400
    
    def test_login_missing_password_should_fail(self):
        payload = {
            'email': self.__email
        }
        response = post('/session', payload)

        assert response[0] == 400
    
    def test_login_wrong_email_should_fail(self):
        payload = {
            'email': 'some-random-email@email.com',
            'password': self.__password
        }
        response = post('/session', payload)

        assert response[0] == 403
    
    def test_login_wrong_password_should_fail(self):
        payload = {
            'email': self.__email,
            'password': 'some-random-password'
        }
        response = post('/session', payload)

        assert response[0] == 403
    
    def test_create_student_same_email_should_fail(self):
        payload = {
            'name': self.__name,
            'email': self.__email,
            'password': self.__password
        }
        response = post('/students', payload)

        assert response[0] == 500