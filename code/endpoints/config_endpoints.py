from flask import abort
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

class ConfigEndpoints:
    def __init__(self, api: Api, config_service: ConfigService):
        api.add_namespace(_namespace)
        ConfigsResource._config_service = config_service

    def register_resources(self) -> None:
        _namespace.add_resource(ConfigsResource, '')
