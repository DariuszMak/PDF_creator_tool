from marshmallow import Schema, fields


class PlainUserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    surname = fields.Str(required=True)
    email = fields.Str(required=True)


class PlainCompanySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class UserSchema(PlainUserSchema):
    company_id = fields.Int(required=True, load_only=True)
    company = fields.Nested(PlainCompanySchema(), dump_only=True)
    password = fields.Str(required=True, load_only=True)


class UserRegisterSchema(PlainUserSchema):
    company = fields.Nested(PlainCompanySchema(), dump_only=True)
    password = fields.Str(required=True, load_only=True)


class UserLoginSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class UserUpdateSchema(Schema):
    name = fields.Str()
    surname = fields.Str()
    email = fields.Str()
    password = fields.Str()
    company_id = fields.Int(allow_none=True)


class CompanySchema(PlainCompanySchema):
    users = fields.List(fields.Nested(PlainUserSchema()), dump_only=True)
