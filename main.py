from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, time
from sqlalchemy import  func, extract, DateTime
from flask_login import LoginManager



from configs.base_config import Config ,Development, Testing, Production

app = Flask(__name__)
login_manager = LoginManager()

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://postgres:nyanumba@127.0.0.1:5433/duka"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config.from_object(Production) 


db = SQLAlchemy(app)
class Products(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True, autoincrement = True, nullable=False)
    name = db.Column(db.String(80), unique=True)
    bp = db.Column(db.Numeric(15), unique=True)
    sp = db.Column(db.Numeric(15), unique=True)
    serial_no = db.Column(db.Integer, unique=True)

class Sales(db.Model):
    __tablename__ = 'sales'
    id = db.Column(db.Integer, primary_key=True, autoincrement = True, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), autoincrement = True)
    quantity = db.Column(db.Integer, unique=False)
    created_at = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
     
   
    product = db.relationship('Products', backref=db.backref('sales', lazy=True))



@app.route('/')
def home():
    return render_template('index.html')

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
    labels = []
    data = []
    for i in data:
        labels.append(i[0])
        data.append(int(i[1]))
        print(data,labels)
    return render_template('dashboard.html', labels= labels, data = data)



if __name__ == "__main__":
    app.run(debug=True)    