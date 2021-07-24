from  sqlalchemy import  Sequence
from settings import db
from werkzeug.security import generate_password_hash, check_password_hash
from .product_size import ProductSize
from sqlalchemy.schema import FetchedValue
class Product(db.Model):
    id = db.Column(db.Integer,Sequence('id_seq'), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    price = db.Column(db.Integer) #in cents
    description = db.Column(db.String(500))
    image = db.Column(db.String(100))
    categories = db.relationship('Category', secondary='product_category')
    orders = db.relationship('Order_Item', backref='product', lazy=True)
    sizes = db.relationship('Size', secondary='product_size')
    def set_stock(self,size_id,quantity):
        pz=db.session.query(ProductSize).filter_by(product_id =self.id,size_id=size_id).first() 
        print(pz)
        pz.stock=pz.stock+quantity
        db.session.commit()
    def get_productRe(self):
        products=[ cate.products for cate in self.categories]
        p=[]
        for i in products:
            for g in i:
                if g not in p:
                    p.append(g)
        return set(p)

    def set_classname(self):
        classname=[c.name for c in self.categories]
        listToStr = ' '.join([str(elem) for elem in classname])
        return listToStr
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    def get_stock(self):
        return db.session.query(db.func.sum(ProductSize.stock)).filter(ProductSize.product_id == self.id).scalar()
    def get_stock_by_size(self,size_id):
        return db.session.query(db.func.sum(ProductSize.stock)).filter(ProductSize.product_id == self.id,ProductSize.size_id == size_id).scalar()
    def __repr__(self):
        return  '<product {} {} , {}>'.format(self.name,self.price,self.image)