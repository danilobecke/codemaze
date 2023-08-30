from datetime import datetime, timedelta
from io import BytesIO

import pytest

from tests.helper import post, get_manager_id_token, get_random_name, get_new_group_id_code, CONTENT_TYPE_FORM_DATA, get_random_manager_token, get_filepath_of_size, get, get_student_id_token, create_join_request_group_id, patch, create_task_json, create_test_case_json

# pylint: disable=too-many-public-methods
class TestTask:
    @pytest.mark.smoke
    def test_create_task_should_create(self) -> None:
        manager_id_token = get_manager_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_id_token[1])
        payload = {
            'name': get_random_name(),
            'max_attempts': 10,
            'languages': ['c'],
            'starts_on': datetime.now().astimezone().isoformat(),
            'ends_on': (datetime.now().astimezone() + timedelta(days=1)).isoformat(),
            'file': (BytesIO(b'Random file content.'), 'file_name.txt')
        }
        response = post(f'/api/v1/groups/{group_id_code[0]}/tasks', payload, manager_id_token[1], CONTENT_TYPE_FORM_DATA)

        assert response[0] == 201
        json = response[1]
        id = json['id']
        assert json['name'] == payload['name']
        assert json['max_attempts'] == payload['max_attempts']
        assert json['languages'] == payload['languages']
        assert datetime.fromisoformat(str(json['starts_on'])) == datetime.fromisoformat(str(payload['starts_on']))
        assert datetime.fromisoformat(str(json['ends_on'])) == datetime.fromisoformat(str(payload['ends_on']))
        assert json['file_url'] == f'/api/v1/tasks/{id}/task'

    @pytest.mark.smoke
    def test_create_task_without_optional_parameters_should_create_and_set_start_date(self) -> None:
        manager_id_token = get_manager_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_id_token[1])
        payload = {
            'name': get_random_name(),
            'languages': ['c', 'python'],
            'file': (BytesIO(b'Random file content.'), 'file_name.txt')
        }
        response = post(f'/api/v1/groups/{group_id_code[0]}/tasks', payload, manager_id_token[1], CONTENT_TYPE_FORM_DATA)

        assert response[0] == 201
        json = response[1]
        id = json['id']
        assert json['name'] == payload['name']
        assert json['max_attempts'] is None
        assert json['languages'] == payload['languages']
        assert json['starts_on'] is not None
        assert json['ends_on'] is None
        assert json['file_url'] == f'/api/v1/tasks/{id}/task'

    def test_create_task_without_name_should_fail(self) -> None:
        manager_id_token = get_manager_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_id_token[1])
        payload = {
            'languages': ['c'],
            'file': (BytesIO(b'Random file content.'), 'file_name.txt')
        }
        response = post(f'/api/v1/groups/{group_id_code[0]}/tasks', payload, manager_id_token[1], CONTENT_TYPE_FORM_DATA)

        assert response[0] == 400

    def test_create_task_without_languages_should_fail(self) -> None:
        manager_id_token = get_manager_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_id_token[1])
        payload = {
            'name': get_random_name(),
            'languages': [],
            'file': (BytesIO(b'Random file content.'), 'file_name.txt')
        }
        response = post(f'/api/v1/groups/{group_id_code[0]}/tasks', payload, manager_id_token[1], CONTENT_TYPE_FORM_DATA)

        assert response[0] == 400

    def test_create_task_with_invalid_language_should_fail(self) -> None:
        manager_id_token = get_manager_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_id_token[1])
        payload = {
            'name': get_random_name(),
            'languages': ['my_language', 'c'],
            'file': (BytesIO(b'Random file content.'), 'file_name.txt')
        }
        response = post(f'/api/v1/groups/{group_id_code[0]}/tasks', payload, manager_id_token[1], CONTENT_TYPE_FORM_DATA)

        assert response[0] == 400

    def test_create_task_without_file_should_fail(self) -> None:
        manager_id_token = get_manager_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_id_token[1])
        payload = {
            'name': get_random_name(),
            'languages': ['c']
        }
        response = post(f'/api/v1/groups/{group_id_code[0]}/tasks', payload, manager_id_token[1], CONTENT_TYPE_FORM_DATA)

        assert response[0] == 400

    def test_create_task_without_filename_should_fail(self) -> None:
        manager_id_token = get_manager_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_id_token[1])
        payload = {
            'name': get_random_name(),
            'languages': ['c'],
            'file': (BytesIO(b'Random file content.'))
        }
        response = post(f'/api/v1/groups/{group_id_code[0]}/tasks', payload, manager_id_token[1], CONTENT_TYPE_FORM_DATA)

        assert response[0] == 400

    def test_create_task_with_empty_filename_should_return_unprocessable_entity(self) -> None:
        manager_id_token = get_manager_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_id_token[1])
        payload = {
            'name': get_random_name(),
            'languages': ['c'],
            'file': (BytesIO(b'Random file content.'), '')
        }
        response = post(f'/api/v1/groups/{group_id_code[0]}/tasks', payload, manager_id_token[1], CONTENT_TYPE_FORM_DATA)

        assert response[0] == 422

    def test_create_task_with_invalid_extension_should_return_unprocessable_entity(self) -> None:
        manager_id_token = get_manager_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_id_token[1])
        payload = {
            'name': get_random_name(),
            'languages': ['c'],
            'file': (BytesIO(b'Random file content.'), 'file.png')
        }
        response = post(f'/api/v1/groups/{group_id_code[0]}/tasks', payload, manager_id_token[1], CONTENT_TYPE_FORM_DATA)

        assert response[0] == 422

    def test_create_task_with_invalid_ends_on_should_fail(self) -> None:
        manager_id_token = get_manager_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_id_token[1])
        payload = {
            'name': get_random_name(),
            'languages': ['c'],
            'ends_on': (datetime.now().astimezone() - timedelta(days=1)).isoformat(),
            'file': (BytesIO(b'Random file content.'), 'file_name.txt')
        }
        response = post(f'/api/v1/groups/{group_id_code[0]}/tasks', payload, manager_id_token[1], CONTENT_TYPE_FORM_DATA)

        assert response[0] == 400

    def test_create_task_with_closed_group_should_return_forbidden(self) -> None:
        manager_token = get_manager_id_token()[1]
        group_id_code = get_new_group_id_code(get_random_name(), manager_token)
        group_id = group_id_code[0]
        upadte_payload = {
            'active': False
        }
        patch(f'/api/v1/groups/{group_id}', upadte_payload, manager_token)

        payload = {
            'name': get_random_name(),
            'languages': ['c'],
            'file': (BytesIO(b'Random file content.'), 'file_name.txt')
        }
        response = post(f'/api/v1/groups/{group_id}/tasks', payload, manager_token, CONTENT_TYPE_FORM_DATA)

        assert response[0] == 403

    def test_create_task_with_non_manager_should_return_forbidden(self) -> None:
        manager_id_token = get_manager_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_id_token[1])
        random_manager_token = get_random_manager_token()
        payload = {
            'name': get_random_name(),
            'languages': ['c'],
            'file': (BytesIO(b'Random file content.'), 'file_name.txt')
        }
        response = post(f'/api/v1/groups/{group_id_code[0]}/tasks', payload, random_manager_token, CONTENT_TYPE_FORM_DATA)

        assert response[0] == 403

    def test_create_task_with_invalid_group_id_should_return_not_found(self) -> None:
        manager_id_token = get_manager_id_token()
        payload = {
            'name': get_random_name(),
            'languages': ['c'],
            'file': (BytesIO(b'Random file content.'), 'file_name.txt')
        }
        response = post(f'/api/v1/groups/{99999999}/tasks', payload, manager_id_token[1], CONTENT_TYPE_FORM_DATA)

        assert response[0] == 404

    def test_create_task_with_invalid_file_size_should_return_invalid_file_size(self) -> None:
        filepath = get_filepath_of_size(round(1.1 * 1024 * 1024)) # 1.1 MB
        manager_id_token = get_manager_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_id_token[1])
        with open(filepath, 'rb') as file:
            payload = {
                'name': get_random_name(),
                'languages': ['c'],
                'file': (file, 'file_name.txt')
            }
            response = post(f'/api/v1/groups/{group_id_code[0]}/tasks', payload, manager_id_token[1], CONTENT_TYPE_FORM_DATA)

            assert response[0] == 413

    def test_create_task_with_student_member_should_return_unauthorized(self) -> None:
        manager_id_token = get_manager_id_token()
        student_id_token = get_student_id_token()
        group_id = create_join_request_group_id(student_id_token[1], manager_id_token[1], approve=True)
        payload = {
            'name': get_random_name(),
            'file': (BytesIO(b'Random file content.'), 'file_name.txt')
        }

        response = post(f'/api/v1/groups/{group_id}/tasks', payload, student_id_token[1], CONTENT_TYPE_FORM_DATA)

        assert response[0] == 401

    @pytest.mark.smoke
    def test_download_task_should_succeed(self) -> None:
        manager_id_token = get_manager_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_id_token[1])
        content = 'Random file content.'
        payload = {
            'name': get_random_name(),
            'languages': ['c'],
            'file': (BytesIO(content.encode('UTF-8')), 'file_name.txt')
        }
        task = post(f'/api/v1/groups/{group_id_code[0]}/tasks', payload, manager_id_token[1], CONTENT_TYPE_FORM_DATA)[1]

        response = get(task['file_url'], manager_id_token[1], decode_as_json=False)

        assert response[0] == 200
        assert str(response[1]) == content

    def test_download_task_with_manager_and_not_started_task_should_succeed(self) -> None:
        manager_token = get_manager_id_token()[1]
        task = create_task_json(manager_token, starts_on=(datetime.now().astimezone() + timedelta(days=1)).isoformat())

        response = get(task['file_url'], manager_token, decode_as_json=False)

        assert response[0] == 200

    def test_download_task_with_non_manager_should_return_forbidden(self) -> None:
        manager_id_token = get_manager_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_id_token[1])
        random_manager_token = get_random_manager_token()
        payload = {
            'name': get_random_name(),
            'languages': ['c'],
            'file': (BytesIO(b'Random file content.'), 'file_name.txt')
        }
        task = post(f'/api/v1/groups/{group_id_code[0]}/tasks', payload, manager_id_token[1], CONTENT_TYPE_FORM_DATA)[1]

        response = get(task['file_url'], random_manager_token)

        assert response[0] == 403

    def test_download_task_with_student_and_not_started_task_should_return_forbidden(self) -> None:
        manager_token = get_manager_id_token()[1]
        student_token = get_student_id_token()[1]
        group_id = create_join_request_group_id(student_token, manager_token, approve=True)
        task = create_task_json(manager_token, group_id, starts_on=(datetime.now().astimezone() + timedelta(days=10)).isoformat())

        response = get(task['file_url'], student_token)

        assert response[0] == 403

    def test_download_task_with_invalid_task_should_return_not_found(self) -> None:
        manager_id_token = get_manager_id_token()

        response = get(f'/api/v1/tasks/{999999}/task', manager_id_token[1])

        assert response[0] == 404

    def test_download_task_with_non_member_should_return_forbidden(self) -> None:
        manager_id_token = get_manager_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_id_token[1])
        student_id_token = get_student_id_token()
        payload = {
            'name': get_random_name(),
            'languages': ['c'],
            'file': (BytesIO(b'Random file content.'), 'file_name.txt')
        }
        task = post(f'/api/v1/groups/{group_id_code[0]}/tasks', payload, manager_id_token[1], CONTENT_TYPE_FORM_DATA)[1]
        join_payload = {
            'code': group_id_code[1]
        }
        post('/api/v1/groups/join', join_payload, student_id_token[1])

        response = get(task['file_url'], student_id_token[1])

        assert response[0] == 403

    @pytest.mark.smoke
    def test_download_task_with_student_member_should_succeed(self) -> None:
        manager_id_token = get_manager_id_token()
        student_id_token = get_student_id_token()
        group_id = create_join_request_group_id(student_id_token[1], manager_id_token[1], approve=True)
        content = 'Random file content.'
        payload = {
            'name': get_random_name(),
            'languages': ['c'],
            'file': (BytesIO(content.encode('UTF-8')), 'file_name.txt')
        }
        task = post(f'/api/v1/groups/{group_id}/tasks', payload, manager_id_token[1], CONTENT_TYPE_FORM_DATA)[1]

        response = get(task['file_url'], manager_id_token[1], decode_as_json=False)

        assert response[0] == 200
        assert str(response[1]) == content

    @pytest.mark.smoke
    def test_update_task_should_update(self) -> None:
        manager_id_token = get_manager_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_id_token[1])
        payload = {
            'name': get_random_name(),
            'max_attempts': 10,
            'languages': ['c'],
            'starts_on': datetime.now().astimezone().isoformat(),
            'ends_on': (datetime.now().astimezone() + timedelta(days=1)).isoformat(),
            'file': (BytesIO(b'Random file content.'), 'file_name.txt')
        }
        task = post(f'/api/v1/groups/{group_id_code[0]}/tasks', payload, manager_id_token[1], CONTENT_TYPE_FORM_DATA)[1]
        task_id = task['id']

        new_content = 'New content!'
        update_payload = {
            'name': get_random_name(),
            'max_attempts': 5,
            'starts_on': (datetime.now().astimezone() + timedelta(hours=1)).isoformat(),
            'ends_on': (datetime.now().astimezone() + timedelta(days=10)).isoformat(),
            'file': (BytesIO(new_content.encode('UTF-8')), 'file_name.txt')
        }
        response = patch(f'/api/v1/tasks/{task_id}', update_payload, manager_id_token[1], CONTENT_TYPE_FORM_DATA)

        assert response[0] == 200
        json = response[1]
        id = json['id']
        assert task_id == id
        assert json['name'] == update_payload['name']
        assert json['max_attempts'] == update_payload['max_attempts']
        assert json['languages'] == payload['languages']
        assert datetime.fromisoformat(str(json['starts_on'])) == datetime.fromisoformat(str(update_payload['starts_on']))
        assert datetime.fromisoformat(str(json['ends_on'])) == datetime.fromisoformat(str(update_payload['ends_on']))
        assert json['file_url'] == task['file_url']

        download_response = get(json['file_url'], manager_id_token[1], decode_as_json=False)

        assert download_response[0] == 200
        assert str(download_response[1]) == new_content

    @pytest.mark.smoke
    def test_update_task_with_empty_payload_should_succeed(self) -> None:
        manager_id_token = get_manager_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_id_token[1])
        content = 'Random file content.'
        payload = {
            'name': get_random_name(),
            'languages': ['c'],
            'file': (BytesIO(content.encode('UTF-8')), 'file_name.txt')
        }
        task = post(f'/api/v1/groups/{group_id_code[0]}/tasks', payload, manager_id_token[1], CONTENT_TYPE_FORM_DATA)[1]
        task_id = task['id']

        response = patch(f'/api/v1/tasks/{task_id}', {}, manager_id_token[1], CONTENT_TYPE_FORM_DATA)

        assert response[0] == 200
        json = response[1]
        id = json['id']
        assert task_id == id
        assert json['name'] == task['name']
        assert json['max_attempts'] == task['max_attempts']
        assert json['languages'] == task['languages']
        assert json['starts_on'] == task['starts_on']
        assert json['ends_on'] == task['ends_on']
        assert json['file_url'] == task['file_url']

        download_response = get(json['file_url'], manager_id_token[1], decode_as_json=False)

        assert download_response[0] == 200
        assert str(download_response[1]) == content

    def test_update_task_file_with_empty_filename_should_return_unprocessable_entity(self) -> None:
        manager_id_token = get_manager_id_token()
        task_id = create_task_json(manager_id_token[1])['id']
        payload = {
            'file': (BytesIO(b'Random file content.'), '')
        }

        response = patch(f'/api/v1/tasks/{task_id}', payload, manager_id_token[1], CONTENT_TYPE_FORM_DATA)

        assert response[0] == 422

    def test_update_task_file_with_invalid_extension_should_return_unprocessable_entity(self) -> None:
        manager_id_token = get_manager_id_token()
        task_id = create_task_json(manager_id_token[1])['id']
        payload = {
            'file': (BytesIO(b'Random file content.'), 'file.png')
        }

        response = patch(f'/api/v1/tasks/{task_id}', payload, manager_id_token[1], CONTENT_TYPE_FORM_DATA)

        assert response[0] == 422

    def test_update_task_with_invalid_ends_on_should_fail(self) -> None:
        manager_token = get_manager_id_token()[1]
        task_id = create_task_json(manager_token, starts_on=(datetime.now().astimezone() + timedelta(days=2)).isoformat())['id']
        payload = {
            'ends_on': (datetime.now().astimezone() + timedelta(days=1)).isoformat()
        }

        response = patch(f'/api/v1/tasks/{task_id}', payload, manager_token, CONTENT_TYPE_FORM_DATA)

        assert response[0] == 400

    def test_update_task_with_closed_group_should_return_forbidden(self) -> None:
        manager_token = get_manager_id_token()[1]
        group_id = get_new_group_id_code(get_random_name(), manager_token)[0]
        task = create_task_json(manager_token, group_id, starts_on=(datetime.now().astimezone() + timedelta(days=2)).isoformat())
        task_id = task['id']
        upadte_payload = {
            'active': False
        }
        patch(f'/api/v1/groups/{group_id}', upadte_payload, manager_token)

        response = patch(f'/api/v1/tasks/{task_id}', {}, manager_token, CONTENT_TYPE_FORM_DATA)

        assert response[0] == 403

    def test_update_task_with_non_manager_should_return_forbidden(self) -> None:
        manager_id_token = get_manager_id_token()
        task_id = create_task_json(manager_id_token[1])['id']
        random_manager_token = get_random_manager_token()

        response = patch(f'/api/v1/tasks/{task_id}', {}, random_manager_token, CONTENT_TYPE_FORM_DATA)

        assert response[0] == 403

    def test_update_task_with_invalid_id_should_return_not_found(self) -> None:
        manager_id_token = get_manager_id_token()

        response = patch(f'/api/v1/tasks/{999999}', {}, manager_id_token[1], CONTENT_TYPE_FORM_DATA)

        assert response[0] == 404

    def test_update_task_file_with_invalid_file_size_should_return_invalid_file_size(self) -> None:
        filepath = get_filepath_of_size(round(1.1 * 1024 * 1024)) # 1.1 MB
        manager_id_token = get_manager_id_token()
        task_id = create_task_json(manager_id_token[1])['id']
        with open(filepath, 'rb') as file:
            payload = {
                'file': (file, 'file_name.txt')
            }
            response = patch(f'/api/v1/tasks/{task_id}', payload, manager_id_token[1], CONTENT_TYPE_FORM_DATA)

            assert response[0] == 413

    def test_update_task_with_student_member_should_return_unauthorized(self) -> None:
        manager_id_token = get_manager_id_token()
        student_id_token = get_student_id_token()
        create_join_request_group_id(student_id_token[1], manager_id_token[1], approve=True)
        task_id = create_task_json(manager_id_token[1])['id']

        response = patch(f'/api/v1/tasks/{task_id}', {}, student_id_token[1], CONTENT_TYPE_FORM_DATA)

        assert response[0] == 401

    @pytest.mark.smoke
    def test_get_tasks_with_manager_should_succeed_and_return_all_tasks(self) -> None:
        manager_token = get_manager_id_token()[1]
        group_id = get_new_group_id_code(get_random_name(), manager_token)[0]
        task_1 = create_task_json(manager_token, group_id)
        task_2 = create_task_json(manager_token, group_id, (datetime.now().astimezone() + timedelta(days=1)).isoformat())

        response = get(f'/api/v1/groups/{group_id}/tasks', manager_token)

        assert response[0] == 200
        tasks = response[1]['tasks']
        assert len(tasks) == 2
        assert task_1 in tasks
        assert task_2 in tasks

    @pytest.mark.smoke
    def test_get_tasks_with_student_should_succeed_and_return_started_tasks_only(self) -> None:
        manager_token = get_manager_id_token()[1]
        student_token = get_student_id_token()[1]
        group_id = create_join_request_group_id(student_token, manager_token, approve=True)
        task_1 = create_task_json(manager_token, group_id)
        task_2 = create_task_json(manager_token, group_id, (datetime.now().astimezone() + timedelta(days=1)).isoformat())
        create_task_json(manager_token) # another group

        response = get(f'/api/v1/groups/{group_id}/tasks', student_token)

        assert response[0] == 200
        tasks = response[1]['tasks']
        assert len(tasks) == 1
        assert task_1 in tasks
        assert task_2 not in tasks

    @pytest.mark.smoke
    def test_get_tasks_with_group_without_tasks_should_return_empty_array(self) -> None:
        manager_token = get_manager_id_token()[1]
        group_id = get_new_group_id_code(get_random_name(), manager_token)[0]

        response = get(f'/api/v1/groups/{group_id}/tasks', manager_token)

        assert response[0] == 200
        tasks = response[1]['tasks']
        assert len(tasks) == 0

    def test_get_tasks_with_invalid_group_should_return_not_found(self) -> None:
        manager_token = get_manager_id_token()[1]

        response = get(f'/api/v1/groups/{99999999}/tasks', manager_token)

        assert response[0] == 404

    def test_get_tasks_with_non_manager_should_return_forbidden(self) -> None:
        manager_token = get_manager_id_token()[1]
        group_id = get_new_group_id_code(get_random_name(), manager_token)[0]
        random_manager = get_random_manager_token()

        response = get(f'/api/v1/groups/{group_id}/tasks', random_manager)

        assert response[0] == 403

    def test_get_tasks_with_not_approved_student_should_return_forbidden(self) -> None:
        manager_token = get_manager_id_token()[1]
        student_token = get_student_id_token()[1]
        group_id = create_join_request_group_id(student_token, manager_token)

        response = get(f'/api/v1/groups/{group_id}/tasks', student_token)

        assert response[0] == 403

    @pytest.mark.smoke
    def test_get_task_details_with_manager_should_succeed(self) -> None:
        manager_token = get_manager_id_token()[1]
        task_id = create_task_json(manager_token)['id']
        open_test = create_test_case_json(manager_token, task_id, closed=False)
        closed_test = create_test_case_json(manager_token, task_id, closed=True)

        response = get(f'/api/v1/tasks/{task_id}', manager_token)

        assert response[0] == 200
        task = response[1]
        assert task['id'] == task_id
        assert task['name'] is not None
        assert task['starts_on'] is not None
        assert task['file_url'] is not None
        open_tests = task['open_tests']
        assert len(open_tests) == 1
        assert open_tests[0] == open_test
        assert open_tests[0]['input_url'] is not None
        assert open_tests[0]['output_url'] is not None
        closed_tests = task['closed_tests']
        assert len(closed_tests) == 1
        assert closed_tests[0] == closed_test
        assert closed_tests[0]['input_url'] is not None
        assert closed_tests[0]['output_url'] is not None

    @pytest.mark.smoke
    def test_get_task_details_with_student_should_succeed(self) -> None:
        manager_token = get_manager_id_token()[1]
        student_token = get_student_id_token()[1]
        group_id = create_join_request_group_id(student_token, manager_token, approve=True)
        task_id = create_task_json(manager_token, group_id)['id']
        open_test = create_test_case_json(manager_token, task_id, closed=False)
        closed_test = create_test_case_json(manager_token, task_id, closed=True)

        response = get(f'/api/v1/tasks/{task_id}', student_token)

        assert response[0] == 200
        task = response[1]
        assert task['id'] == task_id
        assert task['name'] is not None
        assert task['starts_on'] is not None
        assert task['file_url'] is not None
        open_tests = task['open_tests']
        assert len(open_tests) == 1
        assert open_tests[0] == open_test
        assert open_tests[0]['input_url'] is not None
        assert open_tests[0]['output_url'] is not None
        closed_tests = task['closed_tests']
        assert len(closed_tests) == 1
        assert closed_tests[0].get('input_url') is None
        assert closed_tests[0].get('output_url') is None
        del closed_test['input_url']
        del closed_test['output_url']
        assert closed_tests[0] == closed_test

    @pytest.mark.smoke
    def test_get_task_details_when_there_are_no_tests_should_return_empty_array(self) -> None:
        manager_token = get_manager_id_token()[1]
        task_id = create_task_json(manager_token)['id']

        response = get(f'/api/v1/tasks/{task_id}', manager_token)

        assert response[0] == 200
        task = response[1]
        assert len(task['open_tests']) == 0
        assert len(task['closed_tests']) == 0

    def test_get_task_details_with_non_manager_should_return_forbidden(self) -> None:
        manager_token = get_manager_id_token()[1]
        task_id = create_task_json(manager_token)['id']
        random_manager = get_random_manager_token()

        response = get(f'/api/v1/tasks/{task_id}', random_manager)

        assert response[0] == 403

    def test_get_task_details_with_student_not_member_should_return_forbidden(self) -> None:
        manager_token = get_manager_id_token()[1]
        student_token = get_student_id_token()[1]
        group_id = create_join_request_group_id(student_token, manager_token, approve=False)
        task_id = create_task_json(manager_token, group_id)['id']

        response = get(f'/api/v1/tasks/{task_id}', student_token)

        assert response[0] == 403

    def test_get_task_details_with_invalid_id_should_return_not_found(self) -> None:
        manager_token = get_manager_id_token()[1]

        response = get(f'/api/v1/tasks/{999999}', manager_token)

        assert response[0] == 404

    @pytest.mark.smoke
    def test_get_task_details_with_manager_with_future_task_should_succeed(self) -> None:
        manager_token = get_manager_id_token()[1]
        task_id = create_task_json(manager_token, starts_on=(datetime.now().astimezone() + timedelta(days=1)).isoformat())['id']
        open_test = create_test_case_json(manager_token, task_id, closed=False)

        response = get(f'/api/v1/tasks/{task_id}', manager_token)

        assert response[0] == 200
        task = response[1]
        assert task['id'] == task_id
        assert task['name'] is not None
        assert task['starts_on'] is not None
        assert task['file_url'] is not None
        open_tests = task['open_tests']
        assert len(open_tests) == 1
        assert open_tests[0] == open_test
        assert open_tests[0]['input_url'] is not None
        assert open_tests[0]['output_url'] is not None

    def test_get_task_details_with_student_with_future_task_should_return_forbidden(self) -> None:
        manager_token = get_manager_id_token()[1]
        student_token = get_student_id_token()[1]
        group_id = create_join_request_group_id(student_token, manager_token, approve=True)
        task_id = create_task_json(manager_token, group_id, (datetime.now().astimezone() + timedelta(days=1)).isoformat())['id']

        response = get(f'/api/v1/tasks/{task_id}', student_token)

        assert response[0] == 403
