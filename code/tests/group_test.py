from tests.helper import post, get, patch
from tests.helper import get_manager_id_token, get_student_id_token, get_random_manager_token, get_new_group_code
import uuid

class TestGroup:
    __group_name = str(uuid.uuid1())

    def test_create_group_should_create(self):
        id_token = get_manager_id_token()
        payload = {
            'name': self.__group_name
        }
        response = post('/groups', payload, id_token[1])

        assert response[0] == 200
        json = response[1]
        assert json['id'] is not None
        assert json['name'] == self.__group_name
        assert json['active'] is True
        assert json['code'] is not None
        assert json['manager_id'] == id_token[0]
    
    def test_create_group_without_name_should_fail(self):
        id_token = get_manager_id_token()
        payload = {
        }
        response = post('/groups', payload, id_token[1])

        assert response[0] == 400
    
    def test_create_group_with_student_should_fail(self):
        id_token = get_student_id_token()
        payload = {
            'name': str(uuid.uuid1())
        }
        response = post('/groups', payload, id_token[1])

        assert response[0] == 401

    def test_create_group_without_token_should_fail(self):
        payload = {
            'name': str(uuid.uuid1())
        }
        response = post('/groups', payload)

        assert response[0] == 401
    
    def test_manager_get_all_groups_should_return_all(self):
        name = str(uuid.uuid1())
        random_token = get_random_manager_token()
        get_new_group_code(name, random_token)
        manager_id_token = get_manager_id_token()

        response = get('/groups', manager_id_token[1])

        assert response[0] == 200
        groups = response[1]['groups']
        assert len(groups) > 0
        # must contain groups owned by others
        assert len(list(filter(lambda json: json['name'] == name, groups))) == 1
    
    def test_manager_get_all_groups_where_member_of_should_return_groups_where_is_member(self):
        manager_id_token = get_manager_id_token()

        response = get('/groups?member_of=true', manager_id_token[1])

        assert response[0] == 200
        groups = response[1]['groups']
        assert len(groups) > 0
        # must contain groups owned by current user
        filtered = list(filter(lambda json: json['manager_id'] == manager_id_token[0], groups))
        assert filtered == groups

    def test_get_all_groups_without_token_should_fail(self):
        response = get('/groups')

        assert response[0] == 401