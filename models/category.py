from  sqlalchemy import  Sequence
from settings import db
class Category(db.Model):
    id = db.Column(db.Integer,Sequence('id_seq'), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    description = db.Column(db.String(500))
    image = db.Column(db.String(100),nullable=True)
    products = db.relationship('Product', secondary='product_category')
