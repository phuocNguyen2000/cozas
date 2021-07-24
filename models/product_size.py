from  sqlalchemy import  Sequence
from settings import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.schema import FetchedValue
class ProductSize(db.Model):
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'),primary_key=True)
    size_id = db.Column(db.Integer, db.ForeignKey('size.id'),primary_key=True)
    stock=db.Column(db.Integer,default=0)