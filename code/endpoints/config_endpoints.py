from flask import abort, send_file
from flask.wrappers import Response
from flask_restx import Api, Resource, Namespace, fields

from endpoints.models.configs_vo import ConfigsVO
from helpers.exceptions import ServerError
from helpers.unwrapper import unwrap
from services.config_service import ConfigService

_namespace = Namespace('configs', description='')

_language_config = _namespace.model('Language Config', {
    'language_name': fields.String(required=True),
    'supported_extensions': fields.List(fields.String, required=True),
    'help': fields.String(attribute='_help', required=True)
})

_config_model = _namespace.model('Configs', {
    'create_test_script_url': fields.String(required=True),
    'configs': fields.Nested(_language_config, skip_none=True, as_list=True, required=True)
})

class ConfigsResource(Resource): # type: ignore
    _config_service: ConfigService | None = None

    @_namespace.doc(description='Get information about supported programming languages.')
    @_namespace.response(500, 'Server error')
    @_namespace.marshal_with(_config_model)
    def get(self) -> ConfigsVO:
        try:
            return unwrap(ConfigsResource._config_service).get_configs()
        except ServerError as e:
            abort(500, str(e))

class DownloadCreateTestScriptResource(Resource): # type: ignore
    _config_service: ConfigService | None = None

    @_namespace.doc(description='Downloads a python script to help create test cases.')
    @_namespace.response(200, 'Success')
    @_namespace.response(500, 'Error')
    def get(self) -> Response:
        try:
            name, path = unwrap(DownloadCreateTestScriptResource._config_service).get_name_path_create_test_script()
            return send_file(path, download_name=name)
        except ServerError as e:
            abort(500, str(e))

class ConfigEndpoints:
    def __init__(self, api: Api, config_service: ConfigService):
        api.add_namespace(_namespace)
        ConfigsResource._config_service = config_service
        DownloadCreateTestScriptResource._config_service = config_service

    def register_resources(self) -> None:
        _namespace.add_resource(ConfigsResource, '')
        _namespace.add_resource(DownloadCreateTestScriptResource, '/create_test_script')
