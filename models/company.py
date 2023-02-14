from db import db


class CompanyModel(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    users = db.relationship("UserModel", back_populates="company", lazy="dynamic")
