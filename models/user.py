from  sqlalchemy import  Sequence
from settings import db

from werkzeug.security import generate_password_hash, check_password_hash
class User(db.Model):
    user_id = db.Column(db.Integer,Sequence('user_id_seq'),primary_key=True,)
    first_name = db.Column(db.String(64), index=True,nullable=False)
    last_name =  db.Column(db.String(64), index=True,nullable=False)
    email =  db.Column(db.String(128), index=True,unique=True,nullable=False)
    password =  db.Column(db.String(128), index=True,nullable=False)
    typea=db.Column(db.String(64), index=True,nullable=False,default='user')

    orders = db.relationship("Order", back_populates="user")

    
    def __repr__(self):
        return  '<User full name {} {} ,email {}>'.format(self.first_name,self.last_name,self.email)
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)