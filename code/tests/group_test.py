from tests.helper import post, get, patch
from tests.helper import get_random_name, get_manager_id_token, get_student_id_token, get_random_manager_token, get_new_group_id_code, create_expired_token

class TestGroup:
    def test_create_group_should_create(self):
        name = get_random_name()
        id_token = get_manager_id_token()
        payload = {
            'name': name
        }
        response = post('/groups', payload, id_token[1])

        assert response[0] == 200
        json = response[1]
        assert json['id'] is not None
        assert json['name'] == name
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

    def test_manager_get_all_groups_where_member_of_when_is_not_member_should_return_empty_list(self):
        random_token = get_random_manager_token()

        response = get('/groups?member_of=true', random_token)

        assert response[0] == 200
        groups = response[1]['groups']
        assert len(groups) == 0

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

    def test_student_join_group_should_work(self):
        student_token = get_student_id_token()[1]
        manager_token = get_manager_id_token()[1]
        group_code = get_new_group_id_code(get_random_name(), manager_token)[1]

        payload = {
            'code': group_code
        }
        response = post('/groups/join', payload, student_token)

        assert response[0] == 200
    
    def test_manager_join_group_should_return_unauthorized(self):
        random_manager_token = get_random_manager_token()
        manager_token = get_manager_id_token()[1]
        group_code = get_new_group_id_code(get_random_name(), manager_token)[1]

        payload = {
            'code': group_code
        }
        response = post('/groups/join', payload, random_manager_token)

        assert response[0] == 401

    def test_join_group_without_token_should_return_unauthorized(self):
        manager_token = get_manager_id_token()[1]
        group_code = get_new_group_id_code(get_random_name(), manager_token)[1]

        payload = {
            'code': group_code
        }
        response = post('/groups/join', payload)

        assert response[0] == 401

    def test_join_group_with_invalid_code_should_return_not_found(self):
        student_token = get_student_id_token()[1]
        group_code = 'invalid'

        payload = {
            'code': group_code
        }
        response = post('/groups/join', payload, student_token)

        assert response[0] == 404

    def test_join_group_twice_should_return_conflict(self):
        student_token = get_student_id_token()[1]
        manager_token = get_manager_id_token()[1]
        group_code = get_new_group_id_code(get_random_name(), manager_token)[1]

        payload = {
            'code': group_code
        }
        response = post('/groups/join', payload, student_token)
        assert response[0] == 200

        response_replay = post('/groups/join', payload, student_token)
        assert response_replay[0] == 409

    def test_manager_get_requests_list_sould_return_requests(self):
        manager_token = get_manager_id_token()[1]
        student_id_token = get_student_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_token)

        payload = {
            'code': group_id_code[1]
        }
        post('groups/join', payload, student_id_token[1])
        response = get(f'groups/{group_id_code[0]}/requests', manager_token)

        assert response[0] == 200
        requests = response[1]['requests']
        assert len(requests) == 1
        assert requests[0]['id'] == student_id_token[0]
        assert requests[0]['student'] == 'Student'
    
    def test_manager_get_requests_list_when_there_is_no_request_should_return_empty_list(self):
        manager_token = get_manager_id_token()[1]
        group_id_code = get_new_group_id_code(get_random_name(), manager_token)

        response = get(f'groups/{group_id_code[0]}/requests', manager_token)

        assert response[0] == 200
        requests = response[1]['requests']
        assert len(requests) == 0
    
    def test_student_get_requests_list_should_return_unauthorized(self):
        manager_token = get_manager_id_token()[1]
        student_id_token = get_student_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_token)

        payload = {
            'code': group_id_code[1]
        }
        post('groups/join', payload, student_id_token[1])
        response = get(f'groups/{group_id_code[0]}/requests', student_id_token[1])

        assert response[0] == 401

    def test_get_requests_list_without_token_should_return_unauthorized(self):
        manager_token = get_manager_id_token()[1]
        group_id_code = get_new_group_id_code(get_random_name(), manager_token)

        response = get(f'groups/{group_id_code[0]}/requests')

        assert response[0] == 401

    def test_get_requests_list_when_is_not_owner_should_return_forbidden(self):
        manager_token = get_manager_id_token()[1]
        random_token = get_random_manager_token()
        group_id_code = get_new_group_id_code(get_random_name(), random_token)

        response = get(f'groups/{group_id_code[0]}/requests', manager_token)

        assert response[0] == 403

    def test_get_requests_list_with_invalid_id_should_return_not_found(self):
        manager_token = get_manager_id_token()[1]
        id = 999999999999999999999

        response = get(f'groups/{id}/requests', manager_token)

        assert response[0] == 404

    def test_manager_approve_join_request_should_work(self):
        manager_token = get_manager_id_token()[1]
        student_id_token = get_student_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_token)

        join_payload = {
            'code': group_id_code[1]
        }
        post('groups/join', join_payload, student_id_token[1])
        request_id = get(f'groups/{group_id_code[0]}/requests', manager_token)[1]['requests'][0]['id']
        payload = {
            'approve': True
        }
        response = patch(f'/groups/{group_id_code[0]}/requests/{request_id}', payload, manager_token)

        assert response[0] == 200
        requests = get(f'groups/{group_id_code[0]}/requests', manager_token)[1]['requests']
        assert len(requests) == 0

    def test_manager_decline_join_request_should_work(self):
        manager_token = get_manager_id_token()[1]
        student_id_token = get_student_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_token)

        join_payload = {
            'code': group_id_code[1]
        }
        post('groups/join', join_payload, student_id_token[1])
        request_id = get(f'groups/{group_id_code[0]}/requests', manager_token)[1]['requests'][0]['id']
        payload = {
            'approve': False
        }
        response = patch(f'/groups/{group_id_code[0]}/requests/{request_id}', payload, manager_token)

        assert response[0] == 200
        requests = get(f'groups/{group_id_code[0]}/requests', manager_token)[1]['requests']
        assert len(requests) == 0

    def test_student_approve_join_request_should_return_unauthorized(self):
        manager_token = get_manager_id_token()[1]
        student_id_token = get_student_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_token)

        join_payload = {
            'code': group_id_code[1]
        }
        post('groups/join', join_payload, student_id_token[1])
        request_id = get(f'groups/{group_id_code[0]}/requests', manager_token)[1]['requests'][0]['id']
        payload = {
            'approve': True
        }
        response = patch(f'/groups/{group_id_code[0]}/requests/{request_id}', payload, student_id_token[1])

        assert response[0] == 401

    def test_approve_join_request_without_token_should_return_unauthorized(self):
        manager_token = get_manager_id_token()[1]
        student_id_token = get_student_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_token)

        join_payload = {
            'code': group_id_code[1]
        }
        post('groups/join', join_payload, student_id_token[1])
        request_id = get(f'groups/{group_id_code[0]}/requests', manager_token)[1]['requests'][0]['id']
        payload = {
            'approve': True
        }
        response = patch(f'/groups/{group_id_code[0]}/requests/{request_id}', payload)

        assert response[0] == 401

    def test_approve_join_request_when_is_not_owner_should_return_forbidden(self):
        random_manager_token = get_random_manager_token()
        manager_token = get_manager_id_token()[1]
        student_id_token = get_student_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), random_manager_token)

        join_payload = {
            'code': group_id_code[1]
        }
        post('groups/join', join_payload, student_id_token[1])
        request_id = get(f'groups/{group_id_code[0]}/requests', random_manager_token)[1]['requests'][0]['id']
        payload = {
            'approve': True
        }
        response = patch(f'/groups/{group_id_code[0]}/requests/{request_id}', payload, manager_token)

        assert response[0] == 403

    def test_approve_join_request_when_group_id_is_not_valid_should_return_not_found(self):
        manager_token = get_manager_id_token()[1]
        id = 999999999999999999999

        payload = {
            'approve': True
        }
        response = patch(f'/groups/{id}/requests/{id}', payload, manager_token)

        assert response[0] == 404

    def test_approve_join_request_when_request_id_is_not_valid_should_return_not_found(self):
        manager_token = get_manager_id_token()[1]
        group_id_code = get_new_group_id_code(get_random_name(), manager_token)
        id = 999999999999999999999

        payload = {
            'approve': True
        }
        response = patch(f'/groups/{group_id_code[0]}/requests/{id}', payload, manager_token)

        assert response[0] == 404

    def test_approve_join_request_twice_should_return_not_found(self):
        manager_token = get_manager_id_token()[1]
        student_id_token = get_student_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_token)

        join_payload = {
            'code': group_id_code[1]
        }
        post('groups/join', join_payload, student_id_token[1])
        request_id = get(f'groups/{group_id_code[0]}/requests', manager_token)[1]['requests'][0]['id']
        payload = {
            'approve': True
        }
        response = patch(f'/groups/{group_id_code[0]}/requests/{request_id}', payload, manager_token)
        assert response[0] == 200

        second_response = patch(f'/groups/{group_id_code[0]}/requests/{request_id}', payload, manager_token)
        assert second_response[0] == 404

    def test_decline_join_request_twice_should_return_not_found(self):
        manager_token = get_manager_id_token()[1]
        student_id_token = get_student_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_token)

        join_payload = {
            'code': group_id_code[1]
        }
        post('groups/join', join_payload, student_id_token[1])
        request_id = get(f'groups/{group_id_code[0]}/requests', manager_token)[1]['requests'][0]['id']
        payload = {
            'approve': False
        }
        response = patch(f'/groups/{group_id_code[0]}/requests/{request_id}', payload, manager_token)
        assert response[0] == 200

        second_response = patch(f'/groups/{group_id_code[0]}/requests/{request_id}', payload, manager_token)
        assert second_response[0] == 404

    def test_manager_get_students_list_should_return_students(self):
        manager_token = get_manager_id_token()[1]
        student_id_token = get_student_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_token)

        join_payload = {
            'code': group_id_code[1]
        }
        post('groups/join', join_payload, student_id_token[1])
        request_id = get(f'groups/{group_id_code[0]}/requests', manager_token)[1]['requests'][0]['id']
        payload = {
            'approve': True
        }
        patch(f'/groups/{group_id_code[0]}/requests/{request_id}', payload, manager_token)
        response = get(f'/groups/{group_id_code[0]}/students', manager_token)

        assert response[0] == 200
        students = response[1]['students']
        assert len(students) == 1
        assert students[0]['name'] == 'Student'
        assert students[0]['email'] == 'student@email.com'

    def test_manager_get_students_list_without_approved_students_should_return_empty_list(self):
        manager_token = get_manager_id_token()[1]
        student_id_token = get_student_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_token)

        join_payload = {
            'code': group_id_code[1]
        }
        post('groups/join', join_payload, student_id_token[1])
        response = get(f'/groups/{group_id_code[0]}/students', manager_token)

        assert response[0] == 200
        students = response[1]['students']
        assert len(students) == 0

    def test_student_get_students_list_should_return_unauthorized(self):
        manager_token = get_manager_id_token()[1]
        student_id_token = get_student_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_token)

        join_payload = {
            'code': group_id_code[1]
        }
        post('groups/join', join_payload, student_id_token[1])
        request_id = get(f'groups/{group_id_code[0]}/requests', manager_token)[1]['requests'][0]['id']
        payload = {
            'approve': True
        }
        patch(f'/groups/{group_id_code[0]}/requests/{request_id}', payload, manager_token)
        response = get(f'/groups/{group_id_code[0]}/students', student_id_token[1])

        assert response[0] == 401

    def test_get_students_list_without_token_should_return_unauthorized(self):
        manager_token = get_manager_id_token()[1]
        group_id_code = get_new_group_id_code(get_random_name(), manager_token)

        response = get(f'/groups/{group_id_code[0]}/students')

        assert response[0] == 401

    def test_get_students_list_when_is_not_owner_should_return_forbidden(self):
        manager_token = get_manager_id_token()[1]
        student_id_token = get_student_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_token)
        random_manager_token = get_random_manager_token()

        join_payload = {
            'code': group_id_code[1]
        }
        post('groups/join', join_payload, student_id_token[1])
        request_id = get(f'groups/{group_id_code[0]}/requests', manager_token)[1]['requests'][0]['id']
        payload = {
            'approve': True
        }
        patch(f'/groups/{group_id_code[0]}/requests/{request_id}', payload, manager_token)
        response = get(f'/groups/{group_id_code[0]}/students', random_manager_token)

        assert response[0] == 403

    def test_get_students_list_with_invalid_id_should_return_not_found(self):
        manager_token = get_manager_id_token()[1]
        id = 999999999999999999999

        response = get(f'/groups/{id}/students', manager_token)

        assert response[0] == 404

    def test_student_get_all_groups_where_member_of_should_return_groups_where_is_member(self):
        manager_id_token = get_manager_id_token()
        student_id_token = get_student_id_token()
        name = get_random_name()
        group_id_code = get_new_group_id_code(name, manager_id_token[1])

        join_payload = {
            'code': group_id_code[1]
        }
        post('groups/join', join_payload, student_id_token[1])
        request_id = get(f'groups/{group_id_code[0]}/requests', manager_id_token[1])[1]['requests'][0]['id']
        payload = {
            'approve': True
        }
        patch(f'/groups/{group_id_code[0]}/requests/{request_id}', payload, manager_id_token[1])
        response = get('/groups?member_of=true', student_id_token[1])

        assert response[0] == 200
        all_groups = get('/groups?member_of=false', student_id_token[1])[1]['groups']
        assert len(all_groups) > len(response[1]['groups'])

    def test_get_groups_list_with_invalid_token_should_return_unauthorized(self):
        token ='invalid'

        response = get('/groups', token)

        assert response[0] == 401

    def test_get_groups_list_with_expired_token_should_return_unauthorized(self):
        manager_id = get_manager_id_token()[0]
        token = create_expired_token(manager_id)

        response = get('/groups', token)

        assert response[0] == 401