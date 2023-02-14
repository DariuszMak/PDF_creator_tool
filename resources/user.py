from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from passlib.hash import pbkdf2_sha256

from db import db
from models import CompanyModel, UserModel
from schemas import UserSchema, UserUpdateSchema, UserLoginSchema, UserRegisterSchema

blp = Blueprint("Users", "users", description="Operations on users")


@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserRegisterSchema)
    def post(self, user_data):
        if UserModel.query.filter(UserModel.name == user_data["name"]).first():
            abort(409, message="A user with that user already exists.")

        user = UserModel(
            name=user_data["name"],
            surname=user_data["surname"],
            email=user_data["email"],
            company_id="",
            password=pbkdf2_sha256.hash(user_data["password"]),
        )
        db.session.add(user)
        db.session.commit()

        return {"message": "User created successfully."}, 201


@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserLoginSchema)
    def post(self, user_data):
        user = UserModel.query.filter(
            UserModel.name == user_data["name"]
        ).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=user.id)
            return {"access_token": access_token}, 200

        abort(401, message="Invalid credentials.")


@blp.route("/user/<int:user_id>")
class User(MethodView):
    @jwt_required()
    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user

    @jwt_required()
    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted."}, 200

    @jwt_required()
    @blp.arguments(UserUpdateSchema)
    @blp.response(200, UserSchema)
    def put(self, user_data, user_id):
        if len(UserModel.query.join(CompanyModel).filter(CompanyModel.id == user_data.get("company_id")).all()):
            abort(409, message="A user is already associated with a company.")

        companies_assigned_to_user = UserModel.query.join(CompanyModel).filter(
            UserModel.id == user_id).all()
        number_of_companies_assigned_to_user = len(companies_assigned_to_user)

        if number_of_companies_assigned_to_user >= 1:
            user = UserModel.query.get(user_id)
            user.company_id = None
            db.session.add(user)
            db.session.commit()

            CompanyModel.query.filter(CompanyModel.id == companies_assigned_to_user[0].id).delete()
            db.session.commit()
            return user

        user = self.update_user_data(user_data, user_id)

        return user

    def update_user_data(self, user_data, user_id):
        user = UserModel.query.get(user_id)
        if user:
            user.name = user_data["name"]
            user.surname = user_data["surname"]
            user.email = user_data["email"]
            user.password = user_data["password"]
            if not user.company_id and CompanyModel.query.get(user_data.get("company_id")):
                user.company_id = user_data.get("company_id")
        else:
            user = UserModel(id=user_id, **user_data)
        db.session.add(user)
        db.session.commit()
        return user


@blp.route("/user")
class UserList(MethodView):
    @jwt_required()
    @blp.response(200, UserSchema(many=True))
    @blp.paginate()
    def get(self, pagination_parameters):
        user_model = UserModel
        pagination_parameters.item_count = user_model.query.count()
        return UserModel.query.paginate(page=pagination_parameters.page, per_page=pagination_parameters.page_size,
                                        error_out=True).items

    @jwt_required()
    @blp.arguments(UserSchema)
    @blp.response(201, UserSchema)
    def post(self, user_data):
        UserModel(
            name=user_data["name"],
            surname=user_data["surname"],
            email=user_data["email"],
            company_id=user_data["company_id"],
            password=user_data["password"],
        )
        user = UserModel(**user_data)

        try:
            db.session.add(user)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the user.")

        return user
