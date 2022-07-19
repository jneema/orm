from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, time
from sqlalchemy import  func, extract, DateTime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, EmailField
from wtforms.validators import ValidationError, DataRequired, InputRequired, Length, Email, EqualTo
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt



from configs.base_config import Base, Development, Staging, Production



app = Flask(__name__)

app.config['SECRET_KEY']='LongAndRandomSecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://wqsvbcbvszvkxi:de81e26baa5b0b4a8d7ec3ec0cbc0e9617d8a8e9a20cc9c62de166118ab6945a@ec2-54-76-43-89.eu-west-1.compute.amazonaws.com:5432/dccs4uikrqga4a"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
app.config.from_object(Production) 

flask_bcrypt = Bcrypt(app)
db = SQLAlchemy(app)


pw_hash = flask_bcrypt.generate_password_hash('form.user.password').decode('utf-8')
flask_bcrypt.check_password_hash(pw_hash, 'form.user.password') # returns True


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = "user"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=False, nullable=False)
    password = db.Column(db.String(300), nullable=False, unique=True)

class Products(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True, autoincrement = True, nullable=False)
    name = db.Column(db.String(80), unique=True)
    bp = db.Column(db.Numeric(15), unique=False)
    sp = db.Column(db.Numeric(15), unique=False)
    serial_no = db.Column(db.Integer, unique=False)

class Sales(db.Model):
    __tablename__ = 'sales'
    id = db.Column(db.Integer, primary_key=True, autoincrement = True, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), autoincrement = True)
    quantity = db.Column(db.Integer, unique=False)
    created_at = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
     
   
    product = db.relationship('Products', backref=db.backref('sales', lazy=True))

class SignUp(FlaskForm):
    username = StringField(label=('Enter Username:'),
    validators=[DataRequired(), Length(max=64)])
    # message='Name length should be %(min)d and %(max)dcharacters'
    email = StringField(label=('Email'), 
        validators=[DataRequired(), 
        Email(), 
        Length(max=120)])
    password = PasswordField(label=('Password'), 
        validators=[DataRequired(), 
        Length(min=8, message='Password should be at least %(min)d characters long')])
    confirm_password = PasswordField(
        label=('Confirm Password'), 
        validators=[DataRequired(message='*Required'),
        EqualTo('password', message='Both password fields must be equal!')])


    submit = SubmitField(label=('Submit'))

    def validate_username(self, username):
        excluded_chars = " *?!'^+%&/()=}][{$#1234567890"
        existing_user_username = User.query.filter_by(
            username=username.data).first() 
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')
        for char in self.username.data:
            if char in excluded_chars:
                raise ValidationError(
                    f"Character {char} is not allowed in username.")
    def validate_email(self, email):
        existing_user_email = User.query.filter_by(
                email=email.data).first()
        if existing_user_email:
            raise ValidationError(
                'That email already exists. Please choose a different one.')   


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=2,max=20)],
    render_kw={"placeholder": "Username"})
    email = EmailField(validators=[InputRequired()],
    render_kw={"placeholder":"Enter Email"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], 
    render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

db.create_all()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/home')
def base():
    return render_template('base.html')
@app.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # check if user exists in the db
        user = User.query.filter_by(username=form.username.data).first()

        # if the user exists check their password
        if user:
            # bcrypt will check the users password and form password to see if they match
            if flask_bcrypt.check_password_hash(user.password, form.password.data):
                # if the passwords match then login the user
                login_user(user)
                return redirect(url_for('base'))
    return render_template('login.html', form=form)      


@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET','POST'])
def signup():
    form = SignUp()

    if form.validate_on_submit():
        hashed_password = flask_bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)    

@app.route('/inventories', methods=['GET', 'POST'])
def inventories():
    if request.method == 'POST':
        name = request.form['name']
        bp = request.form['bp']
        sp = request.form['sp']
        serial_no = request.form['serial_no']

        u = Products(name = name, bp = bp, sp =sp, serial_no = serial_no)
        db.session.add(u)
        db.session.commit()
        print("Record successfully added")
        
        # print(row)
        return redirect(url_for('inventories'))
    else:    
        products = Products.query.all()
        return render_template('inventories.html', products = products)
@app.route('/sales/<string:x>')
def sales(x):
    # cur.execute('SELECT products.name, SUM(sales.quantity) as Quantity, SUM((products.sp-products.bp)*sales.quantity) as Profit FROM sales 
    # INNER JOIN products ON products.id = sales.product_id WHERE product_id=%s GROUP BY products.name', [pid])
    
    # db.session.query(Folder, File)
    # .join(File, Folder.id == File.folder_id)
    # .all()
    r = db.session.query(Products.name, db.func.sum(Sales.quantity).label("Quantity"),db.func.sum((Products.sp-Products.bp)*Sales.quantity).label("Profit")).join(Sales, Products.id == Sales.product_id).group_by(Products.name).filter(Products.id==x).all()
    
    # sales = Sales.query.all()
    return render_template('sales.html', sales = r)

@app.route('/sales')
def total_sales():
    r = db.session.query(Products.name, db.func.sum(Sales.quantity).label("Quantity"),db.func.sum((Products.sp-Products.bp)*Sales.quantity).label("Profit")).join(Sales, Products.id == Sales.product_id).group_by(Products.name).all()
    for result in r:
        print(' Name:', result[0], 'Quantity:', result[1], 'Profit:', result[2])
    # # print(list_sales)
    # sales = Sales.query.all()
    return render_template('sales.html', sales = r)
        
@app.route('/makesale', methods = ['POST'])
def makesale():

    # query = ('INSERT INTO sales(product_id, quantity, created_at) VALUES(%s, %s, %s)')
    # row = (request.form['pid'], request.form['quantity'], 'NOW()')
    product_id = request.form['pid']
    quantity = request.form['quantity']
    created_at = 'NOW()'

    row = Sales(product_id= product_id, quantity = quantity,created_at=created_at)
    db.session.add(row)
    db.session.commit()

    
    return redirect(url_for('inventories'))

@app.route('/editsale', methods=['POST'])
def editsale():
    # query = ('update products set name =%s, bp =%s, sp=%s, serial_no=%s where id = %s')
    # row = (request.form['name'], request.form['bp'], request.form['sp'], request.form['serial_no'], request.form['id'])
    pid = request.form['id']

    row = Products.query.filter_by(id = pid).one()

    row.name = request.form['name']
    row.bp = request.form['bp']
    row.sp = request.form['sp']
    row.serial_no = request.form['serial_no']

    db.session.merge(row)   
    db.session.commit()

    # row = Products(pid = pid, name = name, bp = bp, sp = sp, serial_no = serial_no)
    
    print(row)
    return redirect(url_for('inventories'))


@app.route('/deletesale',methods=['POST','GET'])
def delete_item():

    pid = request.form['id']
    row = Products.query.filter_by(id = pid).one()
     
    db.session.delete(row)
    db.session.commit()

    return redirect('/inventory')    

@app.route('/dashboard')
def dashboard():
    # cur.execute("SELECT  extract(year from sl.created_at) || '-' || extract(month from sl.created_at) || '-' |
    # | extract(day from sl.created_at)as date, sum((pr.sp-pr.bp)* sl.quantity) as totalprofit FROM public.sales as sl 
    # join products as pr on pr.id=sl.product_id  group by sl.created_at order by sl.created_at ASC")

    # print(x)

    spm = Sales.query.with_entities(func.sum(Sales.quantity * Products.sp), extract('month',Sales.created_at)).join(Products).group_by( extract('month',Sales.created_at)) 
    #convert spm to how chartjs expects
    monthspm=[]
    dataspm=[]
    for x in spm :
        monthspm.append(x[1])
        dataspm.append(int(x[0]))
    print("dataspm" ,dataspm )

    # cur.execute(" SELECT sum(s.quantity * p.sp) AS sales, p.name FROM sales s JOIN products p ON p.id = s.product_id GROUP BY p.name ;")
    sbp = Sales.query.with_entities(func.sum(Sales.quantity * Products.sp), Products.name).join(Products).group_by(Products.name ).order_by(func.sum(Sales.quantity * Products.sp))
    
    namesbp=[]
    salesbp=[]
    for x in sbp:
        namesbp.append(x[1])
        salesbp.append(float(x[0])) 
    print(salesbp) 
  
#   cur.execute("SELECT sum(s.quantity * p.sp) AS sales,DATE(created_at) AS today FROM sales s JOIN products p ON p.id = s.product_id WHERE DATE(created_at) = current_date GROUP BY today;")
    ds =  Sales.query.with_entities(func.sum(Sales.quantity * Products.sp),func.date(Sales.created_at)).join(Products).filter(func.date(Sales.created_at) == date.today()).group_by(func.date(Sales.created_at)) 
                
    dailys = 0
    today = []
    for i in ds:
        dailys=(float(i[0]))
        today=(i[1])
    print(dailys)
    
#   monthly sales
    ms = Sales.query.with_entities(func.sum(Sales.quantity * Products.sp),extract('month',Sales.created_at)).join(Products).filter(extract('month',Sales.created_at) == date.today().month).group_by(extract('month',Sales.created_at)) 
    monthsales = 0
    thismonth = []
    for i in ms:
        monthsales=(float(i[0]))
        thismonth=(i[1])
    print(monthsales)

    #   profit per month   
#   cur.execute("SELECT sum(p.sp - p.bp) AS profit,extract(month from s.created_at) AS monthly FROM sales s JOIN products p ON p.id = s.product_id GROUP BY monthly ORDER BY monthly ;")

    
#   cur.execute('SELECT p.name,sum(s.quantity) AS most_sold FROM sales s JOIN products p ON p.id = s.product_id GROUP BY p.name ORDER BY (sum(s.quantity)) DESC LIMIT 5;')
    prod=[]
    data5=[]
    top5 = Sales.query.with_entities(Products.name, func.sum(Sales.quantity)).join(Products ).group_by(Products.name ).order_by(func.sum(Sales.quantity)).limit(5) 
    
    for i in top5:
        prod.append(i[0])
        data5.append(int(i[1]))
    print(data5)
        

    # labels = []
    # data = []
    # for i in data:
    #     labels.append(i[0])
    #     data.append(int(i[1]))
    #     print(data,labels)
    #     db.session.query(Products.name, db.func.sum(Sales.quantity).label("Quantity"),db.func.sum((Products.sp-Products.bp)*Sales.quantity).label("Profit")).filter(extract('year' 'month' 'day' , Sales).label("Date")).join(Sales, Products.id == Sales.product_id).group_by(Products.name).all()

    return render_template('dashboard.html',prod=prod,data5=data5,dailys = dailys,today=today,monthspm=monthspm,dataspm=dataspm,namesbp=namesbp,salesbp= salesbp,monthsales=monthsales,thismonth=thismonth)



if __name__ == "__main__":
    app.run(debug=True)    