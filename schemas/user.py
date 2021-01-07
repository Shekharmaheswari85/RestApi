from ma import ma
from models.user import UserModel
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import Schema
class UserSchema(Schema):
    class Meta:
        model = UserModel
        load_only = ("password",)
        dump_only = ("id")
        load_instance = True
