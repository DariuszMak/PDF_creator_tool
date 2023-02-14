from db import db


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    surname = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(60), unique=False, nullable=False)
    password = db.Column(db.String(80), unique=True, nullable=False)

    company_id = db.Column(
        db.Integer, db.ForeignKey("companies.id"), unique=False, nullable=True
    )
    company = db.relationship("CompanyModel", back_populates="users")
