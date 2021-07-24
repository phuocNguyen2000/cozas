
from settings import db
class ProductCategory(db.Model):
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'),primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'),primary_key=True)