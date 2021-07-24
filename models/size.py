from  sqlalchemy import  Sequence
from settings import db
class Size(db.Model):
    id = db.Column(db.Integer,Sequence('id_seq'), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    products = db.relationship('Product', secondary='product_size')