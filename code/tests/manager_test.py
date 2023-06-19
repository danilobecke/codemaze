from tests.helper import post
import uuid

class TestManager:
    __name = str(uuid.uuid1())
    __email = f'{__name}@email.com'
    __password = f'pass{__name}'

    def test_create_manager_should_create(self):
        payload = {
            'name': self.__name,
            'email': self.__email,
            'password': self.__password
        }
        response = post('/managers', payload)

        assert response[0] == 200
        json = response[1]
        assert json['id'] is not None
        assert json['name'] == self.__name
        assert json['email'] == self.__email
        assert json['role'] == 'manager'
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
        assert json['role'] == 'manager'
        assert json['token'] is not None
    
    def test_create_manager_missing_name_should_fail(self):
        payload = {
            'email': self.__email,
            'password': self.__password
        }
        response = post('/managers', payload)

        assert response[0] == 400
    
    def test_create_manager_missing_email_should_fail(self):
        payload = {
            'name': self.__name,
            'password': self.__password
        }
        response = post('/managers', payload)

        assert response[0] == 400
    
    def test_create_manager_missing_password_should_fail(self):
        payload = {
            'name': self.__name,
            'email': self.__email
        }
        response = post('/managers', payload)

        assert response[0] == 400
    
    def test_create_manager_same_email_should_fail(self):
        payload = {
            'name': self.__name,
            'email': self.__email,
            'password': self.__password
        }
        response = post('/managers', payload)

        assert response[0] == 500