from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models import CompanyModel, UserModel
from schemas import CompanySchema

blp = Blueprint("Companies", "companies", description="Operations on companies")


@blp.route("/company/<string:company_id>")
class Company(MethodView):
    @jwt_required()
    @blp.response(200, CompanySchema)
    def get(self, company_id):
        company = CompanyModel.query.get_or_404(company_id)
        return company

    @jwt_required()
    def delete(self, company_id):
        company = CompanyModel.query.get_or_404(company_id)
        db.session.delete(company)
        db.session.commit()
        return {"message": "Company deleted"}, 200


@blp.route("/company")
class CompanyList(MethodView):
    @jwt_required()
    @blp.response(200, CompanySchema(many=True))
    @blp.paginate()
    def get(self, pagination_parameters):
        company_model = CompanyModel
        pagination_parameters.item_count = company_model.query.count()
        return CompanyModel.query.paginate(page=pagination_parameters.page, per_page=pagination_parameters.page_size,
                                           error_out=True).items

    @jwt_required()
    @blp.arguments(CompanySchema)
    @blp.response(201, CompanySchema)
    def post(self, company_data):
        identity = get_jwt_identity()
        associated_user = UserModel.query.join(CompanyModel).filter(UserModel.id == identity).first()

        if associated_user:
            abort(409, message="A user is already associated with a company.")

        company = CompanyModel(**company_data)
        try:
            db.session.add(company)
            db.session.commit()
        except IntegrityError:
            abort(
                400,
                message="A company with that name already exists.",
            )
        except SQLAlchemyError:
            abort(500, message="An error occurred creating the company.")

        return company
