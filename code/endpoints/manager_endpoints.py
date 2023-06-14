from flask_restx import Api, Resource, Namespace, fields

class ManagerResource(Resource):
        def post(self):
            print('POST :::')

class ManagerEndpoints:
    def __init__(self, api: Api):
        self.__namespace = Namespace('managers', description='')
        api.add_namespace(self.__namespace)

    def register_resources(self):
        self.__namespace.add_resource(ManagerResource, '')


# model = namespace.model(
#     'Manager',
#     {
#         'id': fields.Integer(required=True),
#         'name': fields.String(required=True),
#     }
# )