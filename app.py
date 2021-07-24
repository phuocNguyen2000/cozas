from flask import  render_template, redirect, url_for, session,request,flash, abort

from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_wtf import FlaskForm
from wtforms import  widgets,StringField, IntegerField, TextAreaField, HiddenField, SelectField,SelectMultipleField

from flask_wtf.file import FileField, FileAllowed
import random

from settings import app, db

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

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

@app.route('/')
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

    if session['user']:
        user = models.User.query.filter_by(email=session['user']).first()
        return render_template('index.html',user=user,categories=categories, products=products,form_cart=form_cart,productscart=productscart ,grand_total=grand_total, grand_total_plus_shipping=grand_total_plus_shipping, quantity_total=quantity_total)
    else:

        return render_template('index.html', products=products,categories=categories,form_cart=form_cart,productscart=productscart ,grand_total=grand_total, grand_total_plus_shipping=grand_total_plus_shipping, quantity_total=quantity_total)

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

@app.route('/product/<id>')
def product(id):
   
    product = models.Product.query.filter_by(id=id).first()
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
    uemail=session['user']
    if uemail:
        user = models.User.query.filter_by(email=uemail).first()
        form = Checkout()
        products, grand_total, grand_total_plus_shipping, quantity_total = handle_cart()

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
                p.set_stock(size_id=size.id,quantity= - product['quantity'])
                
            db.session.add(order)
            db.session.commit()

            session['cart'] = []
            session.modified = True

            return redirect(url_for('index'))

        return render_template('checkout.html', form=form,products=products, grand_total=grand_total, grand_total_plus_shipping=grand_total_plus_shipping, quantity_total=quantity_total)
    else:
        return redirect(url_for('signin'))


@app.route('/admin')
def admin():
    uemail=session['user']
    if uemail:
        user = models.User.query.filter_by(email=uemail).first()
        if user.typea=="admin":
            products = models.Product.query.all()
            sizes = models.Size.query.all()
            products_in_stock = models.ProductSize.query.filter(models.ProductSize.stock > 0).count()
            products_out_stock =models.ProductSize.query.filter(models.ProductSize.stock == 0).count()
            print(products_in_stock)
            orders = models.Order.query.all()
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
    uemail=session['user']
    if uemail:
        user = models.User.query.filter_by(email=uemail).first()
        form = AddProduct()
        if user.typea=="admin":
            categories=models.Category.query.all()
            sizes=models.Size.query.all()
    
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
                new_product = models.Product(name=form.name.data, price=form.price.data,categories=g,sizes=sizes, description=form.description.data, image=image_url)
                
                db.session.add(new_product)
                db.session.commit()
                for s in sizes:
                    pz= models.ProductSize.query.filter_by(product_id=new_product.id,size_id=s.id).first()
                    pz.stock=request.form[s.name]
                    db.session.commit()
                return redirect(url_for('admin'))

            return render_template('admin/add-product.html', admin=True, form=form)
        else:
            abort(403)
    else:
        return redirect(url_for('signin'))

@app.route('/admin/editProduct/', methods=['GET', 'POST'])
def editProduct():
    uemail=session['user']
    if uemail:
        user = models.User.query.filter_by(email=uemail).first()
        form = AddProduct()
        if user.typea=="admin":
            product = models.Product.query.filter_by(id=request.form['pId']).first()
            categories=models.Category.query.all()
            sizes=models.Size.query.all()
    
            a=[(i.id,i.name)  for i in categories]
    
            c=[(i.id,i.name)  for i in sizes]
            form.categories.choices=a
            form.sizes.choices=c
            if form.validate_on_submit():
                image_url = photos.url(photos.save(form.image.data))
                print(image_url)
                g=[]
                l=[]
                
                for c in categories:
                    for i in form.categories.data:
                        if c.id == i:
                            g.append(c) 
                product.name=form.name.data
                product.price=form.price.data
                product.categories=g
                product.sizes=sizes
                product.description=form.description.data
                product.image=image_url
                db.session.commit()
                for s in sizes:
                    pz= models.ProductSize.query.filter_by(product_id=product.id,size_id=s.id).first()
                    pz.stock=request.form[s.name]
                    db.session.commit()
                return redirect(url_for('admin'))

            return render_template('admin/edit-product.html',product=product,user=user, admin=True, form=form)
        else:
            abort(403)
    else:
        return redirect(url_for('signin'))
@app.route('/admin/redirectEdit/<id>', methods=['GET', 'POST'])
def redirectEdit(id):
    uemail=session['user']
    if uemail:
        user = models.User.query.filter_by(email=uemail).first()
        form = AddProduct()
        if user.typea=="admin":
            product = models.Product.query.filter_by(id=id).first()
            categories=models.Category.query.all()
            sizes=models.Size.query.all()
    
            a=[(i.id,i.name)  for i in categories]
    
            c=[(i.id,i.name)  for i in sizes]
            old_cate=[(i.id)  for i in product.categories]
            old_size=[(i.id)  for i in product.sizes]
            form.categories.choices=a
            form.categories.default=old_cate
   
            form.sizes.choices=c
            form.sizes.default=old_size
            form.price.default=product.price
            form.image.default=product.image
            form.description.default=product.description
            form.name.default=product.name
            form.process()       
            return render_template('admin/edit-product.html',product=product, admin=True, form=form)
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