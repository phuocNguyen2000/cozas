from models.order import Order
from models import product, size
from flask import  render_template, redirect, url_for, session,request,flash, abort

from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_wtf import FlaskForm
from wtforms import  widgets,StringField, IntegerField, TextAreaField, HiddenField, SelectField,SelectMultipleField

from flask_wtf.file import FileField, FileAllowed
import random
from datetime import datetime

from settings import app, db
import os
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
app.config['UPLOADED_FILES_DEST'] = os.getcwd()

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

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
    
import models

def handle_cart():
    products = []
    grand_total = 0
    index = 0
    quantity_total = 0

    for item in session['cart']:
        product = models.Product.query.filter_by(id=item['id']).first()

        quantity = int(item['quantity'])
        total = quantity * product.price
        grand_total += total

        quantity_total += quantity
        print(item['sizes'])

        products.append({'id' : product.id, 'name' : product.name, 'price' :  product.price,'size':item['sizes'], 'image' : product.image, 'quantity' : quantity, 'total': total, 'index': index})
        index += 1
    
    grand_total_plus_shipping = grand_total + 1000

    return products, grand_total, grand_total_plus_shipping, quantity_total

@app.route('/', methods=['GET', 'POST'])
def index():
    # session['cart'] = []
    if 'cart' not in session:
        session['cart'] = []
    if 'user' not in session:
        session['user'] =None
    if session['user']:
        user = models.User.query.filter_by(email=session['user']).first()

    productscart, grand_total, grand_total_plus_shipping, quantity_total = handle_cart()
    products =models.Product.query.all()
    categories = models.Category.query.all()
    a=[(i.id,i.name)  for i in categories]
    form_cart = AddToCart()
    if request.method== 'POST':
        str=request.form['search-product']
        if str:
            products=[i for i in products if str in i.name]

    if session['user']:
        user = models.User.query.filter_by(email=session['user']).first()
        return render_template('index.html',user=user,categories=categories, products=products,form_cart=form_cart,productscart=productscart ,grand_total=grand_total, grand_total_plus_shipping=grand_total_plus_shipping, quantity_total=quantity_total)
    else:

        return render_template('index.html', products=products,categories=categories,form_cart=form_cart,productscart=productscart ,grand_total=grand_total, grand_total_plus_shipping=grand_total_plus_shipping, quantity_total=quantity_total)





@app.route('/product/<id>', methods=['GET', 'POST'])
def product(id):
   
    product = models.Product.query.filter_by(id=id).first()
    productscart, grand_total, grand_total_plus_shipping, quantity_total = handle_cart()

    form = AddToCart()

    return render_template('view-product.html', product=product, form=form,productscart=productscart ,grand_total=grand_total, grand_total_plus_shipping=grand_total_plus_shipping, quantity_total=quantity_total)
@app.route('/admin/Products', methods=['GET', 'POST'])
def products():
    # session['cart'] = []
    uemail=session['user']
    if uemail:
        user = models.User.query.filter_by(email=uemail).first()
        if user.typea=="admin":
            products = models.Product.query.all()
            sizes = models.Size.query.all()
            orders = models.Order.query.all()
            products_in_stock = models.ProductSize.query.filter(models.ProductSize.stock > 0).count()
            products_out_stock =models.ProductSize.query.filter(models.ProductSize.stock == 0).count()
            now = datetime.now()
            orders_in_year=Order.byYear(now.year)
            print(orders_in_year[0])
            orders = models.Order.query.all()
            return render_template('admin/products.html',sizes=sizes,products=products)
        else:
            abort(403)
    else:
        return redirect(url_for('signin'))


@app.route('/admin/Orders', methods=['GET', 'POST'])
def orders():
    # session['cart'] = []
    uemail=session['user']
    if uemail:
        user = models.User.query.filter_by(email=uemail).first()
        if user.typea=="admin":
            products = models.Product.query.all()
            sizes = models.Size.query.all()
            orders = models.Order.query.all()
            products_in_stock = models.ProductSize.query.filter(models.ProductSize.stock > 0).count()
            products_out_stock =models.ProductSize.query.filter(models.ProductSize.stock == 0).count()
            now = datetime.now()
            orders_in_year=Order.byYear(now.year)
            print(orders_in_year[0])
            orders = models.Order.query.all()
            return render_template('admin/orders.html',orders=orders)
        else:
            abort(403)
    else:
        return redirect(url_for('signin'))


        

@app.route('/signIn', methods=['GET', 'POST'])
def signin():
    if request.method=="POST":
        email=request.form['email']
        password=request.form['password']
        user = db.session.query(models.User).filter_by(email = email).first()
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
        if (db.session.query(models.User).filter_by(email=email).count() == 0):
            new_user=models.User(first_name=fname,last_name=lname,email=email)
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

@app.route('/quick-add/<id>', methods=['GET', 'POST'])
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

@app.route('/cart', methods=['GET', 'POST'])
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
    uemail=session['user']
    if uemail:
        user = models.User.query.filter_by(email=uemail).first()
        form = Checkout()
        products, grand_total, grand_total_plus_shipping, quantity_total = handle_cart()
        form.email.data=user.email
        form.first_name.data=user.first_name
        form.last_name.data=user.last_name

        if form.validate_on_submit():

            order = models.Order()
            form.populate_obj(order)
            order.reference = ''.join([random.choice('ABCDE') for _ in range(5)])
            order.status = 'PENDING'
            order.user=user
            for product in products:
                order_item = models.Order_Item(quantity=product['quantity'], product_id=product['id'],size=product['size'])
                order.items.append(order_item)
                size= models.Size.query.filter_by(name=product['size']).first()
                p= models.Product.query.filter_by(id=product['id']).first()
                print("p",p.id)
                print("size",size.id)
                p.set_stock(size_id=size.id,quantity= - int(product['quantity']))
                
            db.session.add(order)
            db.session.commit()

            session['cart'] = []
            session.modified = True

            return redirect(url_for('index'))

        return render_template('checkout.html',user=user, form=form,products=products, grand_total=grand_total, grand_total_plus_shipping=grand_total_plus_shipping, quantity_total=quantity_total)
    else:
        return redirect(url_for('signin'))


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    uemail=session['user']
    if uemail:
        user = models.User.query.filter_by(email=uemail).first()
        if user.typea=="admin":
            products = models.Product.query.all()
            sizes = models.Size.query.all()
            orders = models.Order.query.all()
            products_in_stock = models.ProductSize.query.filter(models.ProductSize.stock > 0).count()
            products_out_stock =models.ProductSize.query.filter(models.ProductSize.stock == 0).count()
            now = datetime.now()
            orders_in_year=Order.byYear(now.year)
            print(orders_in_year[0])
            orders = models.Order.query.all()
            return render_template('admin/index.html',sizes=sizes,orders=orders_in_year,products=products,products_in_stock=products_in_stock,products_count=len(products),stock_order=len(orders))
        else:
            abort(403)
    else:
        return redirect(url_for('signin'))
    
@app.errorhandler(403)
def permistion_denied(e):
    return render_template('admin/403page.html'), 403

@app.route('/admin/add', methods=['GET', 'POST'])
def add():
    uemail=session['user']
    if uemail:
        user = models.User.query.filter_by(email=uemail).first()
        form = AddProduct()
        if user.typea=="admin":
            categories = models.Category.query.all()
            sizes = models.Size.query.all()
            if request.method=="POST":
                if request.form['name'] and request.form['desc'] and request.form['price']:
                    if 'file' in request.files:
                        f=request.files['file']
                        image_url=photos.url(photos.save(f))
                        print("ok")
                        g=[]
                        for cate in categories:
                            if 'CateCheck'+str(cate.id) in request.form:
                                g.append(cate)
                                  
                        new_product = models.Product(name=request.form['name'], price=request.form['price'],categories=g,sizes=sizes, description=request.form['desc'], image=image_url)  
                        db.session.add(new_product)
                        db.session.commit()
                        for s in sizes:
                            pz= models.ProductSize.query.filter_by(product_id=new_product.id,size_id=s.id).first()
                            pz.stock=request.form[s.name]
                            db.session.commit()
                        return redirect(url_for('products'))
                else:
                    flash(f'Vui lòng nhập đầy đủ thông tin','danger')
                    return redirect(url_for('add'))         

            return render_template('admin/add-product.html', categories=categories,sizes=sizes)
        else:
            abort(403)
    else:
        return redirect(url_for('signin'))
@app.route('/admin/categories', methods=['GET', 'POST'])
def categories():
    uemail=session['user']
    if uemail:
        user = models.User.query.filter_by(email=uemail).first()
        if user.typea=="admin":
            categories=models.Category.query.all()
            return render_template('admin/categories.html', admin=True, categories=categories)
        else:
            abort(403)
    else:
        return redirect(url_for('signin'))


@app.route('/admin/addCategory', methods=['GET', 'POST'])
def addCategory():
    uemail=session['user']
    if uemail:
        user = models.User.query.filter_by(email=uemail).first()
        if user.typea=="admin":
            if request.method=="POST":
                name = request.form['cate-name']
                desc = request.form['desc']
                if name and desc:
                    new_cate = models.Category(name=name,description=desc)
                    db.session.add(new_cate)
                    db.session.commit()
                else:
                    flash("error") 
                return redirect(url_for('admin'))

            return render_template('admin/add-category.html', admin=True)
        else:
            abort(403)
    else:
        return redirect(url_for('signin'))


@app.route('/admin/editCategory', methods=['GET', 'POST'])
def editCategory():
    uemail=session['user']
    if uemail:
        user = models.User.query.filter_by(email=uemail).first()
        if user.typea=="admin":
            
            if request.method=="POST":
                id = request.form['id']
                name = request.form['cate-name']
                desc = request.form['desc']
                if name and desc:
                    cate = models.Category.query.filter_by(id=id).first()
                    cate.name=name
                    cate.description=desc
                    db.session.commit()
                else:
                    flash("err") 
                return redirect(url_for('categories'))

            return render_template('admin/edit-category.html')
        else:
            abort(403)
    else:
        return redirect(url_for('signin'))

@app.route('/admin/reeditCategory/<id>', methods=['GET', 'POST'])
def reeditCategory(id):
    uemail=session['user']
    if uemail:
        user = models.User.query.filter_by(email=uemail).first()
        if user.typea=="admin":
            cate = models.Category.query.filter_by(id=id).first()
            return render_template('admin/edit-category.html',category=cate)
        else:
            abort(403)
    else:
        return redirect(url_for('signin'))

@app.route('/admin/editProduct/', methods=['GET', 'POST'])
def editProduct():
    uemail=session['user']
    if uemail:
        user = models.User.query.filter_by(email=uemail).first()
        if user.typea=="admin":
            product = models.Product.query.filter_by(id=request.form['pId']).first()
            categories = models.Category.query.all()
            sizes = models.Size.query.all()
            if request.method=="POST":
                if request.form['name'] and request.form['desc'] and request.form['price']:
                    if 'file' in request.files:
                        f=request.files['file']
                        image_url=photos.url(photos.save(f))
                        print("ok")
                        g=[]
                        for cate in categories:
                            if 'CateCheck'+str(cate.id) in request.form:
                                g.append(cate)
                                  
                        product.name=request.form['name']
                        product.price=request.form['price']
                        product.categories=g
                        product.sizes=sizes
                        product.description=request.form['desc']
                        product.image=image_url
                        db.session.commit()
                        for s in sizes:
                            pz= models.ProductSize.query.filter_by(product_id=product.id,size_id=s.id).first()
                            pz.stock=request.form[s.name]
                            db.session.commit()
        
                        return redirect(url_for('products')) 
            return render_template('admin/edit-product.html',product=product,user=user,categories=categories,sizes=sizes)
        else:
            abort(403)
    else:
        return redirect(url_for('signin'))


@app.route('/admin/redirectEdit/<id>', methods=['GET', 'POST'])
def redirectEdit(id):
    uemail=session['user']
    if uemail:
        user = models.User.query.filter_by(email=uemail).first()
        if user.typea=="admin":
            product = models.Product.query.filter_by(id=id).first()
            categories=models.Category.query.all()
            sizes=models.Size.query.all()
            return render_template('admin/edit-product.html',product=product,categories=categories,sizes=sizes)
        else:
            abort(403)
    else:
        return redirect(url_for('signin'))
        
@app.route('/admin/order/<order_id>')
def order(order_id):
    uemail=session['user']
    if uemail:
        user = models.User.query.filter_by(email=uemail).first()
        if user.typea=="admin":
            order = models.Order.query.filter_by(id=int(order_id)).first()

            return render_template('admin/view-order.html', order=order, admin=True)
        else:
            abort(403)
    else:
        return redirect(url_for('signin'))

@app.route('/admin/deleteProduct/<product_id>')
def deleteProduct(product_id):
    uemail=session['user']
    if uemail:
        user = models.User.query.filter_by(email=uemail).first()
        if user.typea=="admin":
            print(product_id)
            product = models.Product.query.filter_by(id=int(product_id)).first()
            product.delete()
            return redirect(url_for('admin'))
        else:
            abort(403)
    else:
        return redirect(url_for('signin'))


if __name__ == '__main__':
    app.run(debug=True)