from datetime import datetime, timedelta
from io import BytesIO

from tests.helper import post, get_manager_id_token, get_random_name, get_new_group_id_code, CONTENT_TYPE_FORM_DATA, get_random_manager_token, get_filepath_of_size

class TestTask:
    def test_create_task_should_create(self):
        manager_id_token = get_manager_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_id_token[1])
        payload = {
            'name': get_random_name(),
            'max_attempts': 10,
            'starts_on': datetime.now().astimezone().isoformat(),
            'ends_on': (datetime.now().astimezone() + timedelta(days=1)).isoformat(),
            'file': (BytesIO(b'Random file content.'), 'file_name.txt')
        }
        response = post(f'/groups/{group_id_code[0]}/tasks', payload, manager_id_token[1], CONTENT_TYPE_FORM_DATA)

        assert response[0] == 200
        json = response[1]
        id = json['id']
        assert json['name'] == payload['name']
        assert json['max_attempts'] == payload['max_attempts']
        assert json['starts_on'] == payload['starts_on']
        assert json['ends_on'] == payload['ends_on']
        assert json['file_url'] == f'/tasks/{id}/task'

    def test_create_task_without_optional_parameters_should_create_and_set_start_date(self):
        manager_id_token = get_manager_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_id_token[1])
        payload = {
            'name': get_random_name(),
            'file': (BytesIO(b'Random file content.'), 'file_name.txt')
        }
        response = post(f'/groups/{group_id_code[0]}/tasks', payload, manager_id_token[1], CONTENT_TYPE_FORM_DATA)

        assert response[0] == 200
        json = response[1]
        id = json['id']
        assert json['name'] == payload['name']
        assert json['max_attempts'] is None
        assert json['starts_on'] is not None
        assert json['ends_on'] is None
        assert json['file_url'] == f'/tasks/{id}/task'

    def test_create_task_without_name_should_fail(self):
        manager_id_token = get_manager_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_id_token[1])
        payload = {
            'file': (BytesIO(b'Random file content.'), 'file_name.txt')
        }
        response = post(f'/groups/{group_id_code[0]}/tasks', payload, manager_id_token[1], CONTENT_TYPE_FORM_DATA)

        assert response[0] == 400

    def test_create_task_without_file_should_fail(self):
        manager_id_token = get_manager_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_id_token[1])
        payload = {
            'name': get_random_name()
        }
        response = post(f'/groups/{group_id_code[0]}/tasks', payload, manager_id_token[1], CONTENT_TYPE_FORM_DATA)

        assert response[0] == 400

    def test_create_task_without_filename_should_fail(self):
        manager_id_token = get_manager_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_id_token[1])
        payload = {
            'name': get_random_name(),
            'file': (BytesIO(b'Random file content.'))
        }
        response = post(f'/groups/{group_id_code[0]}/tasks', payload, manager_id_token[1], CONTENT_TYPE_FORM_DATA)

        assert response[0] == 400

    def test_create_task_with_empty_filename_should_return_unprocessable_entity(self):
        manager_id_token = get_manager_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_id_token[1])
        payload = {
            'name': get_random_name(),
            'file': (BytesIO(b'Random file content.'), '')
        }
        response = post(f'/groups/{group_id_code[0]}/tasks', payload, manager_id_token[1], CONTENT_TYPE_FORM_DATA)

        assert response[0] == 422

    def test_create_task_with_invalid_extension_should_return_unprocessable_entity(self):
        manager_id_token = get_manager_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_id_token[1])
        payload = {
            'name': get_random_name(),
            'file': (BytesIO(b'Random file content.'), 'file.png')
        }
        response = post(f'/groups/{group_id_code[0]}/tasks', payload, manager_id_token[1], CONTENT_TYPE_FORM_DATA)

        assert response[0] == 422

    def test_create_task_with_non_manager_should_return_forbidden(self):
        manager_id_token = get_manager_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_id_token[1])
        random_manager_token = get_random_manager_token()
        payload = {
            'name': get_random_name(),
            'file': (BytesIO(b'Random file content.'), 'file_name.txt')
        }
        response = post(f'/groups/{group_id_code[0]}/tasks', payload, random_manager_token, CONTENT_TYPE_FORM_DATA)

        assert response[0] == 403

    def test_create_task_with_invalid_group_id_should_return_not_found(self):
        manager_id_token = get_manager_id_token()
        payload = {
            'name': get_random_name(),
            'file': (BytesIO(b'Random file content.'), 'file_name.txt')
        }
        response = post(f'/groups/{99999999}/tasks', payload, manager_id_token[1], CONTENT_TYPE_FORM_DATA)

        assert response[0] == 404

    def test_create_task_with_invalid_file_size_should_return_invalid_file_size(self):
        filepath = get_filepath_of_size(round(1.1 * 1024 * 1024)) # 1.1 MB
        manager_id_token = get_manager_id_token()
        group_id_code = get_new_group_id_code(get_random_name(), manager_id_token[1])
        with open(filepath, 'rb') as file:
            payload = {
                'name': get_random_name(),
                'file': (file, 'file_name.txt')
            }
            response = post(f'/groups/{group_id_code[0]}/tasks', payload, manager_id_token[1], CONTENT_TYPE_FORM_DATA)

            assert response[0] == 413
