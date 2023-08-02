from io import BytesIO

from tests.helper import get_manager_id_token, create_task_json, post, CONTENT_TYPE_FORM_DATA, get_filepath_of_size, get_student_id_token, create_join_request_group_id, get_random_manager_token, create_test_case_json, get

# pylint: disable=too-many-public-methods
class TestTCase:
    def test_add_open_test_case_should_succeed_with_urls(self) -> None:
        manager_token = get_manager_id_token()[1]
        task_id = create_task_json(manager_token)['id']
        payload = {
            'input': (BytesIO(b'Input.'), 'input.in'),
            'output': (BytesIO(b'Output.'), 'output.out'),
            'closed': False
        }

        response = post(f'/tasks/{task_id}/tests', payload, manager_token, CONTENT_TYPE_FORM_DATA)

        assert response[0] == 201
        json = response[1]
        test_id = json['id']
        assert json['closed'] is False
        assert json['input_url'] == f'/tests/{test_id}/in'
        assert json['output_url'] == f'/tests/{test_id}/out'

    def test_add_closed_test_case_should_succeed_with_urls(self) -> None:
        manager_token = get_manager_id_token()[1]
        task_id = create_task_json(manager_token)['id']
        payload = {
            'input': (BytesIO(b'Input.'), 'input.in'),
            'output': (BytesIO(b'Output.'), 'output.out'),
            'closed': True
        }

        response = post(f'/tasks/{task_id}/tests', payload, manager_token, CONTENT_TYPE_FORM_DATA)

        assert response[0] == 201
        json = response[1]
        test_id = json['id']
        assert json['closed'] is True
        assert json['input_url'] == f'/tests/{test_id}/in'
        assert json['output_url'] == f'/tests/{test_id}/out'

    def test_add_test_case_without_input_should_return_bad_request(self) -> None:
        manager_token = get_manager_id_token()[1]
        task_id = create_task_json(manager_token)['id']
        payload = {
            'output': (BytesIO(b'Output.'), 'output.out'),
            'closed': True
        }

        response = post(f'/tasks/{task_id}/tests', payload, manager_token, CONTENT_TYPE_FORM_DATA)

        assert response[0] == 400

    def test_add_test_case_without_output_should_return_bad_request(self) -> None:
        manager_token = get_manager_id_token()[1]
        task_id = create_task_json(manager_token)['id']
        payload = {
            'input': (BytesIO(b'Input.'), 'input.in'),
            'closed': True
        }

        response = post(f'/tasks/{task_id}/tests', payload, manager_token, CONTENT_TYPE_FORM_DATA)

        assert response[0] == 400

    def test_add_test_case_without_closed_should_return_bad_request(self) -> None:
        manager_token = get_manager_id_token()[1]
        task_id = create_task_json(manager_token)['id']
        payload = {
            'input': (BytesIO(b'Input.'), 'input.in'),
            'output': (BytesIO(b'Output.'), 'output.out')
        }

        response = post(f'/tasks/{task_id}/tests', payload, manager_token, CONTENT_TYPE_FORM_DATA)

        assert response[0] == 400

    def test_add_test_case_with_invalid_input_extension_should_return_unprocessable_entity(self) -> None:
        manager_token = get_manager_id_token()[1]
        task_id = create_task_json(manager_token)['id']
        payload = {
            'input': (BytesIO(b'Input.'), 'input.png'),
            'output': (BytesIO(b'Output.'), 'output.out'),
            'closed': True
        }

        response = post(f'/tasks/{task_id}/tests', payload, manager_token, CONTENT_TYPE_FORM_DATA)

        assert response[0] == 422

    def test_add_test_case_with_invalid_output_extension_should_return_unprocessable_entity(self) -> None:
        manager_token = get_manager_id_token()[1]
        task_id = create_task_json(manager_token)['id']
        payload = {
            'input': (BytesIO(b'Input.'), 'input.in'),
            'output': (BytesIO(b'Output.'), 'output.csv'),
            'closed': True
        }

        response = post(f'/tasks/{task_id}/tests', payload, manager_token, CONTENT_TYPE_FORM_DATA)

        assert response[0] == 422

    def test_add_test_case_with_invalid_input_size_should_return_invalid_file_size(self) -> None:
        filepath = get_filepath_of_size(round(1.1 * 1024 * 1024)) # 1.1 MB
        manager_token = get_manager_id_token()[1]
        task_id = create_task_json(manager_token)['id']
        with open(filepath, 'rb') as file:
            payload = {
                'input': (file, 'input.in'),
                'output': (BytesIO(b'Output.'), 'output.out'),
                'closed': True
            }
            response = post(f'/tasks/{task_id}/tests', payload, manager_token, CONTENT_TYPE_FORM_DATA)

            assert response[0] == 413

    def test_add_test_case_with_invalid_output_size_should_return_invalid_file_size(self) -> None:
        filepath = get_filepath_of_size(round(1.1 * 1024 * 1024)) # 1.1 MB
        manager_token = get_manager_id_token()[1]
        task_id = create_task_json(manager_token)['id']
        with open(filepath, 'rb') as file:
            payload = {
                'input': (BytesIO(b'Input.'), 'input.in'),
                'output': (file, 'output.out'),
                'closed': True
            }
            response = post(f'/tasks/{task_id}/tests', payload, manager_token, CONTENT_TYPE_FORM_DATA)

            assert response[0] == 413

    def test_add_test_case_with_invalid_id_should_return_not_found(self) -> None:
        manager_token = get_manager_id_token()[1]
        payload = {
            'input': (BytesIO(b'Input.'), 'input.in'),
            'output': (BytesIO(b'Output.'), 'output.out'),
            'closed': False
        }

        response = post(f'/tasks/{99999999}/tests', payload, manager_token, CONTENT_TYPE_FORM_DATA)

        assert response[0] == 404

    def test_add_test_case_with_student_should_return_unauthorized(self) -> None:
        manager_token = get_manager_id_token()[1]
        student_token = get_student_id_token()[1]
        group_id = create_join_request_group_id(student_token, manager_token, approve=True)
        task_id = create_task_json(manager_token, group_id)['id']

        payload = {
            'input': (BytesIO(b'Input.'), 'input.in'),
            'output': (BytesIO(b'Output.'), 'output.out'),
            'closed': False
        }

        response = post(f'/tasks/{task_id}/tests', payload, student_token, CONTENT_TYPE_FORM_DATA)

        assert response[0] == 401

    def test_add_test_case_with_non_manager_should_return_forbidden(self) -> None:
        manager_token = get_manager_id_token()[1]
        task_id = create_task_json(manager_token)['id']
        random_manager = get_random_manager_token()

        payload = {
            'input': (BytesIO(b'Input.'), 'input.in'),
            'output': (BytesIO(b'Output.'), 'output.out'),
            'closed': False
        }

        response = post(f'/tasks/{task_id}/tests', payload, random_manager, CONTENT_TYPE_FORM_DATA)

        assert response[0] == 403

    def test_download_input_output_of_open_test_with_manager_should_succeed(self) -> None:
        manager_id_token = get_manager_id_token()
        content_in = 'Test input.'
        content_out = 'Test output.'
        test_case = create_test_case_json(manager_id_token[1], closed=False, content_in=content_in, content_out=content_out)

        response_in = get(test_case['input_url'], manager_id_token[1], decode_as_json=False)
        response_out = get(test_case['output_url'], manager_id_token[1], decode_as_json=False)

        assert response_in[0] == 200
        assert response_out[0] == 200
        assert str(response_in[1]) == content_in
        assert str(response_out[1]) == content_out

    def test_download_input_output_of_open_test_with_student_should_succeed(self) -> None:
        manager_id_token = get_manager_id_token()
        student_token = get_student_id_token()[1]
        group_id = create_join_request_group_id(student_token, manager_id_token[1], approve=True)
        content_in = 'Test input.'
        content_out = 'Test output.'
        test_case = create_test_case_json(manager_id_token[1], group_id=group_id, closed=False, content_in=content_in, content_out=content_out)

        response_in = get(test_case['input_url'], student_token, decode_as_json=False)
        response_out = get(test_case['output_url'], student_token, decode_as_json=False)

        assert response_in[0] == 200
        assert response_out[0] == 200
        assert str(response_in[1]) == content_in
        assert str(response_out[1]) == content_out

    def test_download_input_output_of_closed_test_with_manager_should_succeed(self) -> None:
        manager_id_token = get_manager_id_token()
        content_in = 'Test input.'
        content_out = 'Test output.'
        test_case = create_test_case_json(manager_id_token[1], closed=True, content_in=content_in, content_out=content_out)

        response_in = get(test_case['input_url'], manager_id_token[1], decode_as_json=False)
        response_out = get(test_case['output_url'], manager_id_token[1], decode_as_json=False)

        assert response_in[0] == 200
        assert response_out[0] == 200
        assert str(response_in[1]) == content_in
        assert str(response_out[1]) == content_out

    def test_download_input_output_of_closed_test_with_student_should_return_forbidden(self) -> None:
        manager_id_token = get_manager_id_token()
        student_token = get_student_id_token()[1]
        group_id = create_join_request_group_id(student_token, manager_id_token[1], approve=True)
        test_case_id = create_test_case_json(manager_id_token[1], group_id=group_id, closed=True)['id']

        response_in = get(f'/tests/{test_case_id}/in', student_token)
        response_out = get(f'/tests/{test_case_id}/out', student_token)

        assert response_in[0] == 403
        assert response_out[0] == 403

    def test_download_input_output_of_open_test_with_non_manager_should_return_forbidden(self) -> None:
        manager_id_token = get_manager_id_token()
        test_case = create_test_case_json(manager_id_token[1], closed=False)
        random_manager = get_random_manager_token()

        response_in = get(test_case['input_url'], random_manager)
        response_out = get(test_case['output_url'], random_manager)

        assert response_in[0] == 403
        assert response_out[0] == 403

    def test_download_input_output_of_open_test_with_student_non_member_should_return_forbidden(self) -> None:
        manager_id_token = get_manager_id_token()
        student_token = get_student_id_token()[1]
        group_id = create_join_request_group_id(student_token, manager_id_token[1])
        test_case = create_test_case_json(manager_id_token[1], group_id=group_id, closed=False)

        response_in = get(test_case['input_url'], student_token)
        response_out = get(test_case['output_url'], student_token)

        assert response_in[0] == 403
        assert response_out[0] == 403

    def test_download_input_output_with_invalid_id_should_return_not_found(self) -> None:
        manager_id_token = get_manager_id_token()

        response_in = get(f'tests/{999999}/in', manager_id_token[1])
        response_out = get(f'tests/{999999}/out', manager_id_token[1])

        assert response_in[0] == 404
        assert response_out[0] == 404

    def test_get_tests_with_manager_should_succeed_with_urls(self) -> None:
        manager_token = get_manager_id_token()[1]
        task_id = create_task_json(manager_token)['id']
        create_test_case_json(manager_token, task_id=task_id, closed=False)
        create_test_case_json(manager_token, task_id=task_id, closed=True)

        response = get(f'/tasks/{task_id}/tests', manager_token)

        assert response[0] == 200
        tests = response[1]['tests']
        assert len(tests) == 2
        assert all(test['input_url'] is not None for test in tests) is True
        assert all(test['output_url'] is not None for test in tests) is True

    def test_get_tests_with_student_should_succeed_with_urls_on_open_tests_only(self) -> None:
        manager_token = get_manager_id_token()[1]
        student_token = get_student_id_token()[1]
        group_id = create_join_request_group_id(student_token, manager_token, approve=True)
        task_id = create_task_json(manager_token, group_id)['id']
        open_test_id = create_test_case_json(manager_token, task_id=task_id, closed=False)['id']
        closed_test_id = create_test_case_json(manager_token, task_id=task_id, closed=True)['id']

        response = get(f'/tasks/{task_id}/tests', student_token)

        assert response[0] == 200
        tests = response[1]['tests']
        assert len(tests) == 2
        open_test = list(filter(lambda test: test['id'] == open_test_id, tests))[0]
        assert open_test['input_url'] is not None
        assert open_test['output_url'] is not None
        closed_test = list(filter(lambda test: test['id'] == closed_test_id, tests))[0]
        assert closed_test['input_url'] is None
        assert closed_test['output_url'] is None

    def test_get_tests_when_task_has_no_tests_should_return_empty_list(self) -> None:
        manager_token = get_manager_id_token()[1]
        student_token = get_student_id_token()[1]
        group_id = create_join_request_group_id(student_token, manager_token, approve=True)
        task_id = create_task_json(manager_token, group_id)['id']

        response_manager = get(f'/tasks/{task_id}/tests', manager_token)
        response_student = get(f'/tasks/{task_id}/tests', student_token)

        assert response_manager[0] == 200
        assert len(response_manager[1]['tests']) == 0
        assert response_student[0] == 200
        assert len(response_student[1]['tests']) == 0

    def test_get_tests_with_non_manager_should_return_forbidden(self) -> None:
        manager_token = get_manager_id_token()[1]
        task_id = create_task_json(manager_token)['id']
        random_manager = get_random_manager_token()

        response = get(f'/tasks/{task_id}/tests', random_manager)

        assert response[0] == 403

    def test_get_tests_with_student_non_member_should_return_forbidden(self) -> None:
        manager_token = get_manager_id_token()[1]
        student_token = get_student_id_token()[1]
        group_id = create_join_request_group_id(student_token, manager_token)
        task_id = create_task_json(manager_token, group_id)['id']

        response = get(f'/tasks/{task_id}/tests', student_token)

        assert response[0] == 403

    def test_get_tests_with_invalid_task_id_should_return_not_found(self) -> None:
        manager_token = get_manager_id_token()[1]

        response = get(f'/tasks/{999999}/tests', manager_token)

        assert response[0] == 404
