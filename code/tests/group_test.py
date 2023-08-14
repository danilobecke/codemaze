import pytest

from tests.helper import post, get, patch, get_random_name, get_manager_id_token, get_student_id_token, get_random_manager_token, get_new_group_id_code, create_expired_token, create_join_request_group_id

# pylint: disable=too-many-public-methods
class TestGroup:
    @pytest.mark.smoke
    def test_create_group_should_create(self) -> None:
        name = get_random_name()
        id_token = get_manager_id_token()
        payload = {
            'name': name
        }
        response = post('/api/v1/groups', payload, id_token[1])

        assert response[0] == 201
        json = response[1]
        assert json['id'] is not None
        assert json['name'] == name
        assert json['active'] is True
        assert json['code'] is not None
        assert json['manager_id'] == id_token[0]

    def test_create_group_without_name_should_return_bad_request(self) -> None:
        id_token = get_manager_id_token()

        response = post('/api/v1/groups', {}, id_token[1])

        assert response[0] == 400

    def test_create_group_with_student_should_return_unauthorized(self) -> None:
        id_token = get_student_id_token()
        payload = {
            'name': get_random_name()
        }
        response = post('/api/v1/groups', payload, id_token[1])

        assert response[0] == 401

    def test_create_group_without_token_should_return_unauthorized(self) -> None:
        payload = {
            'name': get_random_name()
        }
        response = post('/api/v1/groups', payload)

        assert response[0] == 401

    @pytest.mark.smoke
    def test_manager_get_all_groups_should_return_all(self) -> None:
        name = get_random_name()
        random_token = get_random_manager_token()
        get_new_group_id_code(name, random_token)
        manager_id_token = get_manager_id_token()

        response = get('/api/v1/groups', manager_id_token[1])

        assert response[0] == 200
        groups = response[1]['groups']
        assert len(groups) > 0
        # must contain groups owned by others
        assert len(list(filter(lambda json: json['name'] == name, groups))) == 1

    @pytest.mark.smoke
    def test_manager_get_all_groups_where_member_of_should_return_groups_where_is_member(self) -> None:
        manager_id_token = get_manager_id_token()

        response = get('/api/v1/groups?member_of=true', manager_id_token[1])

        assert response[0] == 200
        groups = response[1]['groups']
        assert len(groups) > 0
        # must contain groups owned by current user
        filtered = list(filter(lambda json: json['manager_id'] == manager_id_token[0], groups))
        assert filtered == groups

    @pytest.mark.smoke
    def test_manager_get_all_groups_where_member_of_when_is_not_member_should_return_empty_list(self) -> None:
        random_token = get_random_manager_token()

        response = get('/api/v1/groups?member_of=true', random_token)

        assert response[0] == 200
        groups = response[1]['groups']
        assert len(groups) == 0

    def test_get_all_groups_without_token_should_return_unauthorized(self) -> None:
        response = get('/api/v1/groups')

        assert response[0] == 401

    @pytest.mark.smoke
    def test_manager_get_group_info_should_return_group(self) -> None:
        random_manager_token = get_random_manager_token()
        name = get_random_name()
        random_group_id = get_new_group_id_code(name, random_manager_token)[0]
        manager_token = get_manager_id_token()[1]

        response = get(f'/api/v1/groups/{random_group_id}', manager_token)

        assert response[0] == 200
        json = response[1]
        assert json['id'] is not None
        assert json['name'] == name
        assert json['active'] is True
        assert json['code'] is not None
        assert json['manager_id'] is not None

    @pytest.mark.smoke
    def test_student_get_group_info_should_return_group(self) -> None:
        random_manager_token = get_random_manager_token()
        name = get_random_name()
        random_group_id = get_new_group_id_code(name, random_manager_token)[0]
        student_token = get_student_id_token()[1]

        response = get(f'/api/v1/groups/{random_group_id}', student_token)

        assert response[0] == 200
        json = response[1]
        assert json['id'] is not None
        assert json['name'] == name
        assert json['active'] is True
        assert json['code'] is not None
        assert json['manager_id'] is not None

    def test_get_group_info_with_invalid_id_should_return_not_found(self) -> None:
        manager_token = get_manager_id_token()[1]
        id = 999999999999999999999

        response = get(f'/api/v1/groups/{id}', manager_token)

        assert response[0] == 404

    def test_get_group_info_without_token_should_return_unauthorized(self) -> None:
        random_manager_token = get_random_manager_token()
        id = get_new_group_id_code(get_random_name(), random_manager_token)[0]

        response = get(f'/api/v1/groups/{id}')

        assert response[0] == 401

    @pytest.mark.smoke
    def test_update_group_active_should_update(self) -> None:
        manager_id_token = get_manager_id_token()
        name = get_random_name()
        group_id, code = get_new_group_id_code(name, manager_id_token[1])

        payload = {
            'active': False
        }
        response = patch(f'/api/v1/groups/{group_id}', payload, manager_id_token[1])

        assert response[0] == 200
        group = response[1]
        assert group['active'] is False
        assert group['id'] == group_id
        assert group['name'] == name
        assert group['code'] == code

    @pytest.mark.smoke
    def test_update_group_name_should_update(self) -> None:
        manager_id_token = get_manager_id_token()
        group_id, code = get_new_group_id_code(get_random_name(), manager_id_token[1])
        new_name = 'New name!'

        payload = {
            'name': new_name
        }
        response = patch(f'/api/v1/groups/{group_id}', payload, manager_id_token[1])

        assert response[0] == 200
        group = response[1]
        assert group['active'] is True
        assert group['id'] == group_id
        assert group['name'] == new_name
        assert group['code'] == code

    @pytest.mark.smoke
    def test_update_group_name_active_should_update(self) -> None:
        manager_id_token = get_manager_id_token()
        group_id, code = get_new_group_id_code(get_random_name(), manager_id_token[1])
        new_name = 'New name!'

        payload = {
            'name': new_name,
            'active': False
        }
        response = patch(f'/api/v1/groups/{group_id}', payload, manager_id_token[1])

        assert response[0] == 200
        group = response[1]
        assert group['active'] is False
        assert group['id'] == group_id
        assert group['name'] == new_name
        assert group['code'] == code

    @pytest.mark.smoke
    def test_update_group_with_empty_payload_should_work_and_not_update(self) -> None:
        manager_id_token = get_manager_id_token()
        name = get_random_name()
        group_id, code = get_new_group_id_code(name, manager_id_token[1])

        response = patch(f'/api/v1/groups/{group_id}', {}, manager_id_token[1])

        assert response[0] == 200
        group = response[1]
        assert group['active'] is True
        assert group['id'] == group_id
        assert group['name'] == name
        assert group['code'] == code

    def test_update_group_active_with_invalid_id_should_return_not_found(self) -> None:
        manager_token = get_manager_id_token()[1]
        id = 999999999999999999999

        payload = {
            'active': False
        }
        response = patch(f'/api/v1/groups/{id}', payload, manager_token)

        assert response[0] == 404

    def test_update_group_active_without_being_owner_should_return_forbidden(self) -> None:
        random_manager_token = get_random_manager_token()
        group_id = get_new_group_id_code(get_random_name(), random_manager_token)[0]
        manager_token = get_manager_id_token()[1]

        payload = {
            'active': False
        }
        response = patch(f'/api/v1/groups/{group_id}', payload, manager_token)

        assert response[0] == 403

    def test_update_group_active_without_token_should_return_unauthorized(self) -> None:
        manager_token = get_manager_id_token()[1]
        group_id = get_new_group_id_code(get_random_name(), manager_token)[0]

        payload = {
            'active': False
        }
        response = patch(f'/api/v1/groups/{group_id}', payload)

        assert response[0] == 401

    @pytest.mark.smoke
    def test_student_join_group_should_work(self) -> None:
        student_token = get_student_id_token()[1]
        manager_token = get_manager_id_token()[1]
        group_code = get_new_group_id_code(get_random_name(), manager_token)[1]

        payload = {
            'code': group_code
        }
        response = post('/api/v1/groups/join', payload, student_token)

        assert response[0] == 200

    def test_manager_join_group_should_return_unauthorized(self) -> None:
        random_manager_token = get_random_manager_token()
        manager_token = get_manager_id_token()[1]
        group_code = get_new_group_id_code(get_random_name(), manager_token)[1]

        payload = {
            'code': group_code
        }
        response = post('/api/v1/groups/join', payload, random_manager_token)

        assert response[0] == 401

    def test_join_group_without_token_should_return_unauthorized(self) -> None:
        manager_token = get_manager_id_token()[1]
        group_code = get_new_group_id_code(get_random_name(), manager_token)[1]

        payload = {
            'code': group_code
        }
        response = post('/api/v1/groups/join', payload)

        assert response[0] == 401

    def test_join_group_with_invalid_code_should_return_not_found(self) -> None:
        student_token = get_student_id_token()[1]
        group_code = 'invalid'

        payload = {
            'code': group_code
        }
        response = post('/api/v1/groups/join', payload, student_token)

        assert response[0] == 404

    @pytest.mark.smoke
    def test_join_group_twice_should_return_conflict(self) -> None:
        student_token = get_student_id_token()[1]
        manager_token = get_manager_id_token()[1]
        group_code = get_new_group_id_code(get_random_name(), manager_token)[1]

        payload = {
            'code': group_code
        }
        response = post('/api/v1/groups/join', payload, student_token)
        assert response[0] == 200

        response_replay = post('/api/v1/groups/join', payload, student_token)
        assert response_replay[0] == 409

    @pytest.mark.smoke
    def test_manager_get_requests_list_sould_return_requests(self) -> None:
        manager_token = get_manager_id_token()[1]
        student_id_token = get_student_id_token()
        group_id = create_join_request_group_id(student_id_token[1], manager_token)

        response = get(f'/api/v1/groups/{group_id}/requests', manager_token)

        assert response[0] == 200
        requests = response[1]['requests']
        assert len(requests) == 1
        assert requests[0]['id'] == student_id_token[0]
        assert requests[0]['student'] == 'Student'

    @pytest.mark.smoke
    def test_manager_get_requests_list_when_there_is_no_request_should_return_empty_list(self) -> None:
        manager_token = get_manager_id_token()[1]
        group_id_code = get_new_group_id_code(get_random_name(), manager_token)

        response = get(f'/api/v1/groups/{group_id_code[0]}/requests', manager_token)

        assert response[0] == 200
        requests = response[1]['requests']
        assert len(requests) == 0

    def test_student_get_requests_list_should_return_unauthorized(self) -> None:
        manager_token = get_manager_id_token()[1]
        student_id_token = get_student_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_token)

        payload = {
            'code': group_id_code[1]
        }
        post('/api/v1/groups/join', payload, student_id_token[1])
        response = get(f'/api/v1/groups/{group_id_code[0]}/requests', student_id_token[1])

        assert response[0] == 401

    def test_get_requests_list_without_token_should_return_unauthorized(self) -> None:
        manager_token = get_manager_id_token()[1]
        group_id_code = get_new_group_id_code(get_random_name(), manager_token)

        response = get(f'/api/v1/groups/{group_id_code[0]}/requests')

        assert response[0] == 401

    def test_get_requests_list_when_is_not_owner_should_return_forbidden(self) -> None:
        manager_token = get_manager_id_token()[1]
        random_token = get_random_manager_token()
        group_id_code = get_new_group_id_code(get_random_name(), random_token)

        response = get(f'/api/v1/groups/{group_id_code[0]}/requests', manager_token)

        assert response[0] == 403

    def test_get_requests_list_with_invalid_id_should_return_not_found(self) -> None:
        manager_token = get_manager_id_token()[1]
        id = 999999999999999999999

        response = get(f'/api/v1/groups/{id}/requests', manager_token)

        assert response[0] == 404

    @pytest.mark.smoke
    def test_manager_approve_join_request_should_work(self) -> None:
        manager_token = get_manager_id_token()[1]
        student_id_token = get_student_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_token)

        join_payload = {
            'code': group_id_code[1]
        }
        post('/api/v1/groups/join', join_payload, student_id_token[1])
        request_id = get(f'/api/v1/groups/{group_id_code[0]}/requests', manager_token)[1]['requests'][0]['id']
        payload = {
            'approve': True
        }
        response = patch(f'/api/v1/groups/{group_id_code[0]}/requests/{request_id}', payload, manager_token)

        assert response[0] == 200
        requests = get(f'/api/v1/groups/{group_id_code[0]}/requests', manager_token)[1]['requests']
        assert len(requests) == 0

    @pytest.mark.smoke
    def test_manager_decline_join_request_should_work(self) -> None:
        manager_token = get_manager_id_token()[1]
        student_id_token = get_student_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_token)

        join_payload = {
            'code': group_id_code[1]
        }
        post('/api/v1/groups/join', join_payload, student_id_token[1])
        request_id = get(f'/api/v1/groups/{group_id_code[0]}/requests', manager_token)[1]['requests'][0]['id']
        payload = {
            'approve': False
        }
        response = patch(f'/api/v1/groups/{group_id_code[0]}/requests/{request_id}', payload, manager_token)

        assert response[0] == 200
        requests = get(f'/api/v1/groups/{group_id_code[0]}/requests', manager_token)[1]['requests']
        assert len(requests) == 0

    def test_student_approve_join_request_should_return_unauthorized(self) -> None:
        manager_token = get_manager_id_token()[1]
        student_id_token = get_student_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_token)

        join_payload = {
            'code': group_id_code[1]
        }
        post('/api/v1/groups/join', join_payload, student_id_token[1])
        request_id = get(f'/api/v1/groups/{group_id_code[0]}/requests', manager_token)[1]['requests'][0]['id']
        payload = {
            'approve': True
        }
        response = patch(f'/api/v1/groups/{group_id_code[0]}/requests/{request_id}', payload, student_id_token[1])

        assert response[0] == 401

    def test_approve_join_request_without_token_should_return_unauthorized(self) -> None:
        manager_token = get_manager_id_token()[1]
        student_id_token = get_student_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_token)

        join_payload = {
            'code': group_id_code[1]
        }
        post('/api/v1/groups/join', join_payload, student_id_token[1])
        request_id = get(f'/api/v1/groups/{group_id_code[0]}/requests', manager_token)[1]['requests'][0]['id']
        payload = {
            'approve': True
        }
        response = patch(f'/api/v1/groups/{group_id_code[0]}/requests/{request_id}', payload)

        assert response[0] == 401

    def test_approve_join_request_when_is_not_owner_should_return_forbidden(self) -> None:
        random_manager_token = get_random_manager_token()
        manager_token = get_manager_id_token()[1]
        student_id_token = get_student_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), random_manager_token)

        join_payload = {
            'code': group_id_code[1]
        }
        post('/api/v1/groups/join', join_payload, student_id_token[1])
        request_id = get(f'/api/v1/groups/{group_id_code[0]}/requests', random_manager_token)[1]['requests'][0]['id']
        payload = {
            'approve': True
        }
        response = patch(f'/api/v1/groups/{group_id_code[0]}/requests/{request_id}', payload, manager_token)

        assert response[0] == 403

    def test_approve_join_request_when_group_id_is_not_valid_should_return_not_found(self) -> None:
        manager_token = get_manager_id_token()[1]
        id = 999999999999999999999

        payload = {
            'approve': True
        }
        response = patch(f'/api/v1/groups/{id}/requests/{id}', payload, manager_token)

        assert response[0] == 404

    def test_approve_join_request_when_request_id_is_not_valid_should_return_not_found(self) -> None:
        manager_token = get_manager_id_token()[1]
        group_id_code = get_new_group_id_code(get_random_name(), manager_token)
        id = 999999999999999999999

        payload = {
            'approve': True
        }
        response = patch(f'/api/v1/groups/{group_id_code[0]}/requests/{id}', payload, manager_token)

        assert response[0] == 404

    def test_approve_join_request_twice_should_return_not_found(self) -> None:
        manager_token = get_manager_id_token()[1]
        student_id_token = get_student_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_token)

        join_payload = {
            'code': group_id_code[1]
        }
        post('/api/v1/groups/join', join_payload, student_id_token[1])
        request_id = get(f'/api/v1/groups/{group_id_code[0]}/requests', manager_token)[1]['requests'][0]['id']
        payload = {
            'approve': True
        }
        response = patch(f'/api/v1/groups/{group_id_code[0]}/requests/{request_id}', payload, manager_token)
        assert response[0] == 200

        second_response = patch(f'/api/v1/groups/{group_id_code[0]}/requests/{request_id}', payload, manager_token)
        assert second_response[0] == 404

    def test_decline_join_request_twice_should_return_not_found(self) -> None:
        manager_token = get_manager_id_token()[1]
        student_id_token = get_student_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_token)

        join_payload = {
            'code': group_id_code[1]
        }
        post('/api/v1/groups/join', join_payload, student_id_token[1])
        request_id = get(f'/api/v1/groups/{group_id_code[0]}/requests', manager_token)[1]['requests'][0]['id']
        payload = {
            'approve': False
        }
        response = patch(f'/api/v1/groups/{group_id_code[0]}/requests/{request_id}', payload, manager_token)
        assert response[0] == 200

        second_response = patch(f'/api/v1/groups/{group_id_code[0]}/requests/{request_id}', payload, manager_token)
        assert second_response[0] == 404

    @pytest.mark.smoke
    def test_manager_get_students_list_should_return_students(self) -> None:
        manager_token = get_manager_id_token()[1]
        student_id_token = get_student_id_token()
        group_id = create_join_request_group_id(student_id_token[1], manager_token, approve=True)

        response = get(f'/api/v1/groups/{group_id}/students', manager_token)

        assert response[0] == 200
        students = response[1]['students']
        assert len(students) == 1
        assert students[0]['name'] == 'Student'
        assert students[0]['email'] == 'student@email.com'

    @pytest.mark.smoke
    def test_manager_get_students_list_without_approved_students_should_return_empty_list(self) -> None:
        manager_token = get_manager_id_token()[1]
        student_id_token = get_student_id_token()
        group_id = create_join_request_group_id(student_id_token[1], manager_token)

        response = get(f'/api/v1/groups/{group_id}/students', manager_token)

        assert response[0] == 200
        students = response[1]['students']
        assert len(students) == 0

    def test_student_get_students_list_should_return_unauthorized(self) -> None:
        manager_token = get_manager_id_token()[1]
        student_id_token = get_student_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_token)

        join_payload = {
            'code': group_id_code[1]
        }
        post('/api/v1/groups/join', join_payload, student_id_token[1])
        request_id = get(f'/api/v1/groups/{group_id_code[0]}/requests', manager_token)[1]['requests'][0]['id']
        payload = {
            'approve': True
        }
        patch(f'/api/v1/groups/{group_id_code[0]}/requests/{request_id}', payload, manager_token)
        response = get(f'/api/v1/groups/{group_id_code[0]}/students', student_id_token[1])

        assert response[0] == 401

    def test_get_students_list_without_token_should_return_unauthorized(self) -> None:
        manager_token = get_manager_id_token()[1]
        group_id_code = get_new_group_id_code(get_random_name(), manager_token)

        response = get(f'/api/v1/groups/{group_id_code[0]}/students')

        assert response[0] == 401

    def test_get_students_list_when_is_not_owner_should_return_forbidden(self) -> None:
        manager_token = get_manager_id_token()[1]
        student_id_token = get_student_id_token()
        group_id = create_join_request_group_id(student_id_token[1], manager_token, approve=True)
        random_manager_token = get_random_manager_token()

        response = get(f'/api/v1/groups/{group_id}/students', random_manager_token)

        assert response[0] == 403

    def test_get_students_list_with_invalid_id_should_return_not_found(self) -> None:
        manager_token = get_manager_id_token()[1]
        id = 999999999999999999999

        response = get(f'/api/v1/groups/{id}/students', manager_token)

        assert response[0] == 404

    @pytest.mark.smoke
    def test_student_get_all_groups_where_member_of_should_return_groups_where_is_member(self) -> None:
        manager_id_token = get_manager_id_token()
        student_id_token = get_student_id_token()
        create_join_request_group_id(student_id_token[1], manager_id_token[1], approve=True)

        response = get('/api/v1/groups?member_of=true', student_id_token[1])

        assert response[0] == 200
        all_groups = get('/api/v1/groups?member_of=false', student_id_token[1])[1]['groups']
        assert len(all_groups) > len(response[1]['groups'])

    # JWT tests

    def test_get_groups_list_with_invalid_token_should_return_unauthorized(self) -> None:
        token ='invalid'

        response = get('/api/v1/groups', token)

        assert response[0] == 401

    def test_get_groups_list_with_expired_token_should_return_unauthorized(self) -> None:
        manager_id = get_manager_id_token()[0]
        token = create_expired_token(manager_id)

        response = get('/api/v1/groups', token)

        assert response[0] == 401

    def test_get_groups_list_with_wrong_token_patter_should_return_unauthorized(self) -> None:
        token = get_manager_id_token()[1]

        response = get('/api/v1/groups', custom_headers={'Authorization': f'{token}'})

        assert response[0] == 401
