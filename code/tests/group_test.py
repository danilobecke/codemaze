from tests.helper import post, get, patch
from tests.helper import get_random_name, get_manager_id_token, get_student_id_token, get_random_manager_token, get_new_group_id_code

class TestGroup:
    __group_name = get_random_name()

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
    
    def test_create_group_without_name_should_return_bad_request(self):
        id_token = get_manager_id_token()
        payload = {
        }
        response = post('/groups', payload, id_token[1])

        assert response[0] == 400
    
    def test_create_group_with_student_should_return_unauthorized(self):
        id_token = get_student_id_token()
        payload = {
            'name': get_random_name()
        }
        response = post('/groups', payload, id_token[1])

        assert response[0] == 401

    def test_create_group_without_token_should_return_unauthorized(self):
        payload = {
            'name': get_random_name()
        }
        response = post('/groups', payload)

        assert response[0] == 401
    
    def test_manager_get_all_groups_should_return_all(self):
        name = get_random_name()
        random_token = get_random_manager_token()
        get_new_group_id_code(name, random_token)
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

    def test_get_all_groups_without_token_should_return_unauthorized(self):
        response = get('/groups')

        assert response[0] == 401
    
    def test_manager_get_group_info_should_return_group(self):
        random_manager_token = get_random_manager_token()
        name = get_random_name()
        random_group_id = get_new_group_id_code(name, random_manager_token)[0]
        manager_token = get_manager_id_token()[1]

        response = get(f'/groups/{random_group_id}', manager_token)

        assert response[0] == 200
        json = response[1]
        assert json['id'] is not None
        assert json['name'] == name
        assert json['active'] is True
        assert json['code'] is not None
        assert json['manager_id'] is not None

    def test_student_get_group_info_should_return_group(self):
        random_manager_token = get_random_manager_token()
        name = get_random_name()
        random_group_id = get_new_group_id_code(name, random_manager_token)[0]
        student_token = get_student_id_token()[1]

        response = get(f'/groups/{random_group_id}', student_token)

        assert response[0] == 200
        json = response[1]
        assert json['id'] is not None
        assert json['name'] == name
        assert json['active'] is True
        assert json['code'] is not None
        assert json['manager_id'] is not None

    def test_get_group_info_with_invalid_id_should_return_not_found(self):
        manager_token = get_manager_id_token()[1]
        id = 999999999999999999999

        response = get(f'/groups/{id}', manager_token)

        assert response[0] == 404

    def test_get_group_info_without_token_should_return_unauthorized(self):
        random_manager_token = get_random_manager_token()
        id = get_new_group_id_code(get_random_name(), random_manager_token)[0]

        response = get(f'/groups/{id}')

        assert response[0] == 401

    def test_update_group_active_should_update(self):
        manager_id_token = get_manager_id_token()
        group_id = get_new_group_id_code(get_random_name(), manager_id_token[1])[0]

        payload = {
            'active': False
        }
        response = patch(f'/groups/{group_id}', payload, manager_id_token[1])

        assert response[0] == 200

        group = get(f'/groups/{group_id}', manager_id_token[1])[1]
        assert group['active'] is False

    def test_update_group_active_with_invalid_id_should_return_not_found(self):
        manager_token = get_manager_id_token()[1]
        id = 999999999999999999999

        payload = {
            'active': False
        }
        response = patch(f'/groups/{id}', payload, manager_token)

        assert response[0] == 404

    def test_update_group_active_without_being_owner_should_return_forbidden(self):
        random_manager_token = get_random_manager_token()
        group_id = get_new_group_id_code(get_random_name(), random_manager_token)[0]
        manager_token = get_manager_id_token()[1]

        payload = {
            'active': False
        }
        response = patch(f'/groups/{group_id}', payload, manager_token)

        assert response[0] == 403
    
    def test_update_group_active_without_token_should_return_unauthorized(self):
        manager_token = get_manager_id_token()[1]
        group_id = get_new_group_id_code(get_random_name(), manager_token)[0]

        payload = {
            'active': False
        }
        response = patch(f'/groups/{group_id}', payload)

        assert response[0] == 401