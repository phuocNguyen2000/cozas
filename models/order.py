from datetime import time
from  sqlalchemy import  Sequence
from settings import db
from werkzeug.security import generate_password_hash, check_password_hash
from .order_item import Order_Item
from .product import Product
import datetime
import calendar
class Order(db.Model):
    id = db.Column(db.Integer,Sequence('id_seq'), primary_key=True)
    reference = db.Column(db.String(5))
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    phone_number = db.Column(db.Integer)
    email = db.Column(db.String(50))
    address = db.Column(db.String(100))
    city = db.Column(db.String(100))
    state = db.Column(db.String(20))
    country = db.Column(db.String(20))
    status = db.Column(db.String(10))
    payment_type = db.Column(db.String(10))
    items = db.relationship('Order_Item', backref='order', lazy=True)
    user = db.relationship("User", back_populates="orders")
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    time_created = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())

    @staticmethod
    def byYear(year):
       orders=  db.session.query(db.extract('month', Order.time_created),db.func.count(db.extract('month', Order.time_created)).label("month")).group_by(db.extract('year', Order.time_created),db.extract('month', Order.time_created)).filter(db.extract('year', Order.time_created)==year).all()
       ordersm=[(calendar.month_name[i[0]],i[1]) for i in orders]
       return ordersm
     
    def order_total(self):
        return db.session.query(db.func.sum(Order_Item.quantity * Product.price)).join(Product).filter(Order_Item.order_id == self.id).scalar() + 1000

    def quantity_total(self):
        return db.session.query(db.func.sum(Order_Item.quantity)).filter(Order_Item.order_id == self.id).scalar()