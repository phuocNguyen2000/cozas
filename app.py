from flask import Flask, render_template, redirect, url_for, session,request,flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from  sqlalchemy import  Sequence
from sqlalchemy.orm import defaultload
from werkzeug.security import generate_password_hash, check_password_hash

from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_wtf import FlaskForm
from wtforms import widgets,StringField, IntegerField, TextAreaField, HiddenField, SelectField,SelectMultipleField

from flask_wtf.file import FileField, FileAllowed
import random

app = Flask(__name__)

photos = UploadSet('photos', IMAGES)

app.config['UPLOADED_PHOTOS_DEST'] = 'images'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trendy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'mysecret'

configure_uploads(app, photos)

db = SQLAlchemy(app)
migrate = Migrate(app, db)



class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()
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
        pz=ProductSize.query.filter(ProductSize.product_id == self.id,ProductSize.size_id == size_id)
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
        
class ProductSize(db.Model):
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'),primary_key=True)
    size_id = db.Column(db.Integer, db.ForeignKey('size.id'),primary_key=True)
    stock=db.Column(db.Integer,default=0)

class Category(db.Model):
    id = db.Column(db.Integer,Sequence('id_seq'), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    description = db.Column(db.String(500))
    image = db.Column(db.String(100),nullable=True)
    products = db.relationship('Product', secondary='product_category')

class Size(db.Model):
    id = db.Column(db.Integer,Sequence('id_seq'), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    products = db.relationship('Product', secondary='product_size')

class ProductCategory(db.Model):
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'),primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'),primary_key=True)
   
    
   

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

    def order_total(self):
        return db.session.query(db.func.sum(Order_Item.quantity * Product.price)).join(Product).filter(Order_Item.order_id == self.id).scalar() + 1000

    def quantity_total(self):
        return db.session.query(db.func.sum(Order_Item.quantity)).filter(Order_Item.order_id == self.id).scalar()

class Order_Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer)
class User(db.Model):
    user_id = db.Column(db.Integer,Sequence('user_id_seq'),primary_key=True)
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
class AddProduct(FlaskForm):
    name = StringField('Name')
    price = IntegerField('Price')
    stock = IntegerField('Stock')
    description = TextAreaField('Description')
    image = FileField('Image', validators=[FileAllowed(IMAGES, 'Only images are accepted.')])
    categories =  MultiCheckboxField('Category', coerce=int,render_kw={'style': 'height: fit-content; list-style: none;'})
    sizes =  MultiCheckboxField('Size', coerce=int,render_kw={'style': 'height: fit-content; list-style: none;'})
    

class AddToCart(FlaskForm):
    quantity = IntegerField('Quantity')
    id = HiddenField('ID')

class Checkout(FlaskForm):
    first_name = StringField('First Name')
    last_name = StringField('Last Name')
    phone_number = StringField('Number')
    email = StringField('Email')
    address = StringField('Address')
    city = StringField('City')
    state = SelectField('State', choices=[('CA', 'California'), ('WA', 'Washington'), ('NV', 'Nevada')])
    country = SelectField('Country', choices=[('US', 'United States'), ('UK', 'United Kingdom'), ('FRA', 'France')])
    payment_type = SelectField('Payment Type', choices=[('CK', 'Check'), ('WT', 'Wire Transfer')])

def handle_cart():
    products = []
    grand_total = 0
    index = 0
    quantity_total = 0

    for item in session['cart']:
        product = Product.query.filter_by(id=item['id']).first()

        quantity = int(item['quantity'])
        total = quantity * product.price
        grand_total += total

        quantity_total += quantity
        print(item['sizes'])

        products.append({'id' : product.id, 'name' : product.name, 'price' :  product.price,'size':item['sizes'], 'image' : product.image, 'quantity' : quantity, 'total': total, 'index': index})
        index += 1
    
    grand_total_plus_shipping = grand_total + 1000

    return products, grand_total, grand_total_plus_shipping, quantity_total

@app.route('/')
def index():
    # session['cart'] = []
    if 'cart' not in session:
        session['cart'] = []
    if 'user' not in session:
        session['user'] =None
    if session['user']:
        user = User.query.filter_by(email=session['user']).first()

    productscart, grand_total, grand_total_plus_shipping, quantity_total = handle_cart()
    products = Product.query.all()
    categories = Category.query.all()
    a=[(i.id,i.name)  for i in categories]
    form_cart = AddToCart()

    if session['user']:
        user = User.query.filter_by(email=session['user']).first()
        return render_template('index.html',user=user, products=products,form_cart=form_cart,productscart=productscart ,grand_total=grand_total, grand_total_plus_shipping=grand_total_plus_shipping, quantity_total=quantity_total)
    else:

        return render_template('index.html', products=products,form_cart=form_cart,productscart=productscart ,grand_total=grand_total, grand_total_plus_shipping=grand_total_plus_shipping, quantity_total=quantity_total)

@app.route('/signIn', methods=['GET', 'POST'])
def signin():
    if request.method=="POST":
        email=request.form['email']
        password=request.form['password']
        user = db.session.query(User).filter_by(email = email).first()
        if (user is None):
            flash('Sai Email hoặc mật khẩu!')
        else:
            if(user.check_password(password)):

                session['user'] = user.email
                session['ac-type']=user.typea
                return redirect(url_for('index'))
            else:
                flash('Sai Email hoặc mật khẩu!')
                return render_template('signinpage.html')
    return render_template('signinpage.html')
@app.route('/signUp' ,methods=['GET', 'POST'])
def signup():
    if request.method=="POST":
        fname=request.form['fname']
        lname=request.form['lname']
        email=request.form['email']
        password=request.form['password']
        if (db.session.query(User).filter_by(email=email).count() == 0):
            new_user=User(first_name=fname,last_name=lname,email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            session['user']=email
            session['ac-type']=new_user.typea
            return redirect(url_for('index'))
        else:
            flash('Email {} is alrealy exsits!'.format(email))
            return render_template('signuppage.html')
    return render_template('signuppage.html')
@app.route('/logOut' ,methods=['GET', 'POST'])
def logOut():
    session['user']=None
    session['ac-type']=None
    return redirect(url_for('index'))

@app.route('/product/<id>')
def product(id):
   
    product = Product.query.filter_by(id=id).first()
    productscart, grand_total, grand_total_plus_shipping, quantity_total = handle_cart()

    form = AddToCart()

    return render_template('view-product.html', product=product, form=form,productscart=productscart ,grand_total=grand_total, grand_total_plus_shipping=grand_total_plus_shipping, quantity_total=quantity_total)

@app.route('/quick-add/<id>')
def quick_add(id):
    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append({'id' : id, 'quantity' : 1})
    session.modified = True

    return redirect(url_for('index'))

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    if 'cart' not in session:
        session['cart'] = []

    form = AddToCart()

    if form.validate_on_submit():

        session['cart'].append({'id' : form.id.data,'sizes':request.form['size'], 'quantity' : form.quantity.data})
        session.modified = True
        print(session['cart'])

    return redirect(url_for('index'))

@app.route('/cart')
def cart():
    products, grand_total, grand_total_plus_shipping, quantity_total = handle_cart()

    return render_template('cart.html', products=products, grand_total=grand_total, grand_total_plus_shipping=grand_total_plus_shipping, quantity_total=quantity_total)

@app.route('/remove-from-cart/<index>')
def remove_from_cart(index):
    del session['cart'][int(index)]
    session.modified = True
    return redirect(url_for('index'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    form = Checkout()

    products, grand_total, grand_total_plus_shipping, quantity_total = handle_cart()

    if form.validate_on_submit():

        order = Order()
        form.populate_obj(order)
        order.reference = ''.join([random.choice('ABCDE') for _ in range(5)])
        order.status = 'PENDING'

        for product in products:
            order_item = Order_Item(quantity=product['quantity'], product_id=product['id'])
            order.items.append(order_item)
            size= Size.query.filter_by(name=product['size']).first()
            p= Product.query.filter_by(id=product['id']).first()
            p.set_stock(size_id=size.id,quantity= - product['quantity'])
            

        db.session.add(order)
        db.session.commit()

        session['cart'] = []
        session.modified = True

        return redirect(url_for('index'))

    return render_template('checkout.html', form=form,products=products, grand_total=grand_total, grand_total_plus_shipping=grand_total_plus_shipping, quantity_total=quantity_total)

@app.route('/admin')
def admin():
    uemail=session['user']
    if uemail:
        user = User.query.filter_by(email=uemail).first()
        if user.typea=="admin":
            products = Product.query.all()
            sizes = Size.query.all()
            products_in_stock = ProductSize.query.filter(ProductSize.stock > 0).count()
            products_out_stock = ProductSize.query.filter(ProductSize.stock == 0).count()
            print(products_in_stock)
            orders = Order.query.all()
            return render_template('admin/index.html', admin=True, products=products,products_out_stock=products_out_stock, sizes=sizes,products_in_stock=products_in_stock, orders=orders)
        else:
            abort(403)
    else:
        return redirect(url_for('signin'))
    
@app.errorhandler(403)
def permistion_denied(e):
    return render_template('admin/403page.html'), 403

@app.route('/admin/add', methods=['GET', 'POST'])
def add():
    form = AddProduct()
    categories=Category.query.all()
    sizes=Size.query.all()
    
    a=[(i.id,i.name)  for i in categories]
    
    c=[(i.id,i.name)  for i in sizes]

    form.categories.choices=a
   
    form.sizes.choices=c
    print(form.sizes.choices[0])

    if form.validate_on_submit():
        image_url = photos.url(photos.save(form.image.data))
        print(image_url)
        g=[]
        l=[]
        
        for c in categories:
            for i in form.categories.data:
                if c.id == i:
                    g.append(c) 
        new_product = Product(name=form.name.data, price=form.price.data,categories=g,sizes=sizes, description=form.description.data, image=image_url)
        
        db.session.add(new_product)
        db.session.commit()
        for s in sizes:
            pz= ProductSize.query.filter_by(product_id=new_product.id,size_id=s.id).first()
            pz.stock=request.form[s.name]
            db.session.commit()
        return redirect(url_for('admin'))

    return render_template('admin/add-product.html', admin=True, form=form)

@app.route('/admin/order/<order_id>')
def order(order_id):
    order = Order.query.filter_by(id=int(order_id)).first()

    return render_template('admin/view-order.html', order=order, admin=True)
@app.route('/admin/deleteProduct/<product_id>')
def deleteProduct(product_id):
    print(product_id)
    product = Product.query.filter_by(id=int(product_id)).first()
    product.delete()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)