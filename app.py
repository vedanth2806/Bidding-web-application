from flask import Flask,redirect,render_template,request,session,flash,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate,migrate
from datetime import datetime, date
import os

app = Flask(__name__)
app.app_context().push()

app.config['SECRET_KEY'] = 'your_secret_key'

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///online_aution.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

app.config['UPLOAD_FOLDER'] = 'static/uploads'

db=SQLAlchemy(app)
migrate=Migrate(app,db)

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    firstname=db.Column(db.String(20),nullable=False)
    lastname=db.Column(db.String(15),nullable=False)
    username=db.Column(db.String(20),nullable=False)
    password=db.Column(db.String(20),nullable=False)
    email=db.Column(db.String(50),unique=True,nullable=False)
    phone=db.Column(db.String,nullable=True)
    
    def __repr__(self):
        return f"Name:{self.firstname}, User:{self.username} Email:{self.email}"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        phone = request.form.get("phone")
        
        # Check if the email already exists
        existing_user = User.query.filter_by(email=email).first()
        
        if existing_user:
            flash('Email already exists. Please use a different email.', 'danger')
            return redirect('/register')
        
        # Create a new user if all fields are filled and the email is unique
        if (firstname != '' and lastname != '' and 
            username != '' and password != '' and 
            email != '' and phone != ''):
            
            new_user = User(
                firstname=firstname,
                lastname=lastname,
                username=username,
                password=password, 
                email=email,
                phone=phone
            )
           
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful. Please log in.', 'success')
            return redirect('/login')
        
        flash('All fields are required!', 'danger')
        return redirect('/register')
    
    return render_template('register.html')

@app.route('/delete/<int:id>')
def erase(id):
    data=User.query.get(id)
    db.session.delete(data)
    db.session.commit()
    return redirect('/users')

@app.route('/users')
def userView():
    if 'user_id' not in session:
        return redirect('/login')
    registers=User.query.all()
    return render_template('users.html',registers=registers)

@app.route('/login', methods=['GET', 'POST'])
def log():
    if request.method == 'POST':
        
        username = request.form.get("username")
        password = request.form.get("password")
        
        
        user = User.query.filter_by(username=username, password=password).first()

        if user:
            
            session['user_id'] = user.id
            # flash("Login successful!","success")
            # session['username'] = user.username
            return redirect('/home')
        else:
            
            flash('Invalid username or password', 'danger')
            return redirect('/login')

    return render_template('login.html')

@app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    return redirect('/login')

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float,nullable=False)
    estimated_price = db.Column(db.Float, nullable=False)
    start_from = db.Column(db.Date, nullable=False)
    ends_on = db.Column(db.Date, nullable=False)
    file_path = db.Column(db.String(100),nullable=False)
    description = db.Column(db.Text, nullable=False)
    upload_email = db.Column(db.String, nullable = True)
    bidder_email = db.Column(db.String, nullable = True)
    
    def __repr__(self):
        return f'<Product {self.product_name}>'
    
    
@app.route('/home', methods=['POST','GET'])
def func1():
    if request.method == 'POST':
        product_name = request.form['product_name']
        price = float(request.form['price'])  # Fetch the 'price' from the form
        
        # Convert date strings to Python date objects
        start_from = datetime.strptime(request.form['start_from'], '%Y-%m-%d').date()
        ends_on = datetime.strptime(request.form['ends_on'], '%Y-%m-%d').date()

        description = request.form['description']

        # Handle file upload
        file = request.files['file_path']
        file_path = None
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

        # Set estimated_price to be the same as price
        estimated_price = price

        # Create a new Product instance
        new_product = Product(
            product_name=product_name, 
            price=price,
            estimated_price=estimated_price,  # Same value as price
            start_from=start_from, 
            ends_on=ends_on, 
            description=description, 
            file_path=file_path
        )

        # Add to database and commit
        db.session.add(new_product)
        db.session.commit()

        return redirect(url_for('func1'))
    else:
        today = date.today()
        live_products = Product.query.filter((Product.start_from <= today) & (Product.ends_on>=today))
        featured_products = Product.query.filter(Product.start_from>today)
        recent_products = Product.query.filter(Product.ends_on < today)
        # print(products)
        # img_path= (products.file_path).replace('\','/'')
        # print(img_path)
        return render_template('home.html', L_products=live_products, F_products=featured_products, P_products= recent_products)

@app.route('/upload')
def fun2():
    return render_template('upload.html')

#For deleting items
@app.route('/delete/<int:id>')
def eraseItem(id):
    data=Product.query.get(id)
    db.session.delete(data)
    db.session.commit()
    return redirect('/delete')


@app.route('/delete')
def func3():
    uploads = Product.query.all()
    return render_template('Delete.html',uploads=uploads)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(100), nullable=False)
    mobile=db.Column(db.Integer, nullable=False)
    email=db.Column(db.String(100), nullable=False)
    subject=db.Column(db.String(100), nullable=False)
    message=db.Column(db.String(100), nullable=False)
    
@app.route('/contact',methods=['POST'])
def contactt():
    name=request.form.get("name")
    mobile=request.form.get("mobile")
    email=request.form.get("email")
    subject=request.form.get("subject")
    message=request.form.get("message")

    if name and mobile and email and subject and message is not None:
        p=Contact(name=name,mobile=mobile,email=email,subject=subject,message=message)
        db.session.add(p)
        db.session.commit()
        return redirect('/contact')
    else:
        return redirect('/contact')



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def regi():
    return render_template('register.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/howorks')
def howorks():
    return render_template('howorks.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/FAQs')
def FAQs():
    return render_template('FAQs.html')

@app.route('/work')
def work():
    return render_template('work.html')

@app.route('/contact1')
def contact1():
    return render_template('contact1.html')

@app.route('/bid/<int:id>', methods=['POST'])
def bidding(id):
    if request.method == 'POST':
        p = Product.query.get(id)
        user = User.query.get(session['user_id'])
        bidder_price = float(request.form.get('bid_price'))
        if bidder_price>p.estimated_price:
            p.estimated_price = bidder_price
            p.bidder_email = user.email
            db.session.commit()
            return redirect('/home')
        else:
                 
            return redirect('/home')


@app.route('/profile')
def profile():
    user = User.query.get(session['user_id'])
    email = user.email
    items = Product.query.filter_by(bidder_email=user.email).all()
    return render_template('profile.html' ,user = user, items=items)


@app.route('/')
def func44():
    uploads = Product.query.all()
    return render_template('Delete.html',uploads=uploads)




if __name__ == '__main__':
   
    app.run(debug=True)