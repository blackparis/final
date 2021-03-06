from flask import Flask, render_template, url_for, redirect, request, jsonify, session
from flask_session import Session
from flask_socketio import SocketIO, emit
from werkzeug.security import check_password_hash, generate_password_hash
import random
import requests
from datetime import datetime
import boto3
from flask_session import Session
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
import envs
import util
from models import *
import itertools

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config["SQLALCHEMY_DATABASE_URI"] = envs.DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

app.config["SECRET_KEY"] = envs.SECRET_KEY
socketio = SocketIO(app)

class PhotoForm(FlaskForm):
    photo = FileField('image', validators=[FileRequired()])


def get_products():
    """ Load all products into session """
    if session.get("products") == None:
        session["products"] = {}
        session["categories"] = []
        products = Product.query.order_by(Product.name).all()
        for p in products:
            session["products"][p.name] = {
                "id": p.id,
                "name": p.name,
                "category": p.category,
                "subcategory": p.subcategory,
                "unit": p.unit,
                "price": p.price,
                "stock": p.stock,
                "url": p.imageUrl,
                "display": p.display,
                "info": p.info,
                "tags": None
            }

            tags = Tags.query.filter_by(product_id=p.id).first()
            if tags != None:
                session["products"][p.name]["tags"] = []
                if tags.tag1:
                    session["products"][p.name]["tags"].append(tags.tag1)
                if tags.tag2:
                    session["products"][p.name]["tags"].append(tags.tag2)
                if tags.tag3:
                    session["products"][p.name]["tags"].append(tags.tag3)
                if tags.tag4:
                    session["products"][p.name]["tags"].append(tags.tag4)
                if tags.tag5:
                    session["products"][p.name]["tags"].append(tags.tag5)

            if p.category not in session["categories"]:
                session["categories"].append(p.category)        
    else:
        return


@app.route("/sessionclear")
def sessionclear():
    session.clear()
    return redirect("/")


@app.route("/admin")
def admin():
    if session.get("customer") != None:
        return redirect(url_for('homepage'))
    if not session.get("admin"):
        return redirect(url_for('admin_login'))    
    
    count_open = Order.query.filter_by(status="OPEN").count()
    count_for_cancellaiton = Order.query.filter_by(status="FOR CANCELLATION").count()
    products = Product.query.filter(Product.stock < 10).count()
    return render_template(
        "admin/homepage.html",
        shopname=envs.SHOPNAME,
        admin=session["admin"],
        count_open=count_open,
        count_for_cancellaiton=count_for_cancellaiton,
        products=products
    )


@app.route("/admin/stockupdate", methods=["POST", "GET"])
def admin_stock_update():
    if request.method == "GET":
        #display all stocks that have a value less than 10
        if session.get("customer") != None:
            return redirect(url_for('homepage'))
        if not session.get("admin"):
            return redirect(url_for('admin_login'))
        
        products = Product.query.filter(Product.stock < 10).all()
        return render_template(
            "admin/updatestock.html",
            shopname=envs.SHOPNAME,
            admin=session["admin"],
            products=products
        )
    else:
        if session.get("customer") != None:
            return jsonify({"success": False, "message": "Invalid Request"})
        if not session.get("admin"):
            return jsonify({"success": False, "message": "Invalid Request"})        
        
        #ajax query to update stock value
        pid = request.form.get("pid")
        value = request.form.get("value")

        try:
            pid = int(pid)
            value = int(value)
        except:
            return jsonify({"success": False, "message": "Invalid Request"})

        p = Product.query.get(pid)
        if p == None:
            return jsonify({"success": False, "message": "Invalid Request"})

        if value < 1:
            return jsonify({"success": False, "message": "Invalid Request"})

        p.stock = value
        db.session.commit()
        return jsonify({"success": True, "name": p.name})


@app.route("/admin/products")
def admin_products():
    if session.get("customer") != None:
        return redirect(url_for('homepage'))
    if not session.get("admin"):
        return redirect(url_for('admin_login'))
    
    get_products()
    return render_template("admin/products.html", shopname=envs.SHOPNAME, admin=session["admin"], products=session["products"], categories=session["categories"])


@app.route("/admin/products/details")
def admin_products_details():
    if session.get("customer") != None:
        return redirect(url_for('homepage'))
    if not session.get("admin"):
        return redirect(url_for('admin_login'))
    #Detailed view of all products
    get_products()
    return render_template("admin/detailedproducts.html", shopname=envs.SHOPNAME, admin=session["admin"], products=session["products"], categories=session["categories"])


@app.route("/admin/<name>/tags/edit", methods=["POST", "GET"])
def admin_edit_tags(name):
    if session.get("customer") != None:
        return redirect(url_for('homepage'))
    if not session.get("admin"):
        return redirect(url_for('admin_login'))    
    #edit/add existing tags for existing products
    get_products()
    p = Product.query.filter_by(name=name).first()
    if p == None:
        return redirect(url_for('admin_products_details'))
    
    tags = p.tags
    
    if request.method == "GET":
        return render_template("admin/tags.html", shopname=envs.SHOPNAME, admin=session["admin"], product=p, edit=True, tags=tags[0])

    tag1 = request.form.get("tag1")
    tag2 = request.form.get("tag2")
    tag3 = request.form.get("tag3")
    tag4 = request.form.get("tag4")
    tag5 = request.form.get("tag5")

    if not tag1:
        return render_template("admin/tags.html", shopname=envs.SHOPNAME, admin=session["admin"], product=p, edit=True, tags=tags[0], tag_error="atleast first tag is required")

    tag = Tags.query.filter_by(product_id=p.id).first()
    if tag == None:
        return redirect(url_for('admin'))
    t = []
    tag1 = tag1.strip().lower()
    t.append(tag1)
    tag.tag1 = tag1

    if tag2:
        tag2 = tag2.strip().lower()
        t.append(tag2)
        tag.tag2 = tag2
    else:
        tag.tag2 = None
    
    if tag3:
        tag3 = tag3.strip().lower()
        t.append(tag3)
        tag.tag3 = tag3
    else:
        tag.tag3 = None

    if tag4:        
        tag4 = tag4.strip().lower()
        t.append(tag4)
        tag.tag4 = tag4
    else:
        tag.tag4 = None

    if tag5:
        tag5 = tag5.strip().lower()
        t.append(tag5)
        tag.tag5 = tag5
    else:
        tag.tag5 = None

    db.session.commit()    
    session["products"][p.name]["tags"].clear()
    session["products"][p.name]["tags"] = t
    return redirect(url_for('admin_products_details'))


@app.route("/admin/<name>/tags", methods=["POST", "GET"])
def admin_add_tags(name):    
    if session.get("customer") != None:
        return redirect(url_for('homepage'))
    if not session.get("admin"):
        return redirect(url_for('admin_login'))    
    #add new tags to newly added products that don't have any tags associated with them
    get_products()
    p = Product.query.filter_by(name=name).first()
    if p == None:
        return redirect(url_for('admin_products_details'))
    
    if request.method == "GET":
        return render_template("admin/tags.html", shopname=envs.SHOPNAME, admin=session["admin"], product=p, add=True)

    tag1 = request.form.get("tag1")
    tag2 = request.form.get("tag2")
    tag3 = request.form.get("tag3")
    tag4 = request.form.get("tag4")
    tag5 = request.form.get("tag5")

    if not tag1:
        return render_template("admin/tags.html", shopname=envs.SHOPNAME, admin=session["admin"], product=p, add=True, tag_error="atleast first tag is required")
    
    t = []
    tag1 = tag1.strip().lower()
    t.append(tag1)

    if tag2:
        tag2 = tag2.strip().lower()
        t.append(tag2)
    else:
        tag2 = None
    
    if tag3:
        tag3 = tag3.strip().lower()
        t.append(tag3)
    else:
        tag3 = None

    if tag4:        
        tag4 = tag4.strip().lower()
        t.append(tag4)
    else:
        tag4 = None

    if tag5:
        tag5 = tag5.strip().lower()
        t.append(tag5)
    else:
        tag5 = None

    tags = Tags(product_id=p.id, tag1=tag1, tag2=tag2, tag3=tag3, tag4=tag4, tag5=tag5)
    db.session.add(tags)
    db.session.commit()
    session["products"][p.name]["tags"] = t
    return redirect(url_for('admin_products_details'))


@app.route("/admin/products/add", methods=["POST", "GET"])
def admin_add_product():
    if session.get("customer") != None:
        return redirect(url_for('homepage'))
    if not session.get("admin"):
        return redirect(url_for('admin_login'))    
    #add new products
    get_products()
    if session.get("newproduct") == None:
        session["newproduct"] = {}

    form = PhotoForm()
    if request.method == "GET":
        return render_template("admin/addproduct.html", shopname=envs.SHOPNAME, admin=session["admin"], form=form, product=session["newproduct"])
    
    name = request.form.get("name")
    category = request.form.get("category")
    subcategory = request.form.get("subcategory")
    unit = request.form.get("unit")
    price = request.form.get("price")
    stock = request.form.get("stock")
    display = request.form.get("display")
    info = request.form.get("info")

    if not name or not category or not unit or not price or not stock or not display:
        return render_template("admin/addproduct.html", shopname=envs.SHOPNAME, admin=session["admin"], form=form, add_product_error="fill in all fields marked with *", product=session["newproduct"])

    if display == "True":
        display = True
    else:
        display = False
    
    if info:
        info = info.strip()
    else:
        info = None

    name = name.strip().title()
    category = category.strip().title()
    if subcategory:
        subcategory = subcategory.strip().title()
    else:
        subcategory = None
    unit = unit.strip().title()

    try:
        price = float(price)
        stock = float(stock)
    except:
        return render_template("admin/addproduct.html", shopname=envs.SHOPNAME, admin=session["admin"], form=form, add_product_error="price and stock must have numeric values", product=session["newproduct"])

    if stock < 0 or price < 0:
        return render_template("admin/addproduct.html", shopname=envs.SHOPNAME, admin=session["admin"], form=form, add_product_error="values of price and stock must be greater than or equal to zero", product=session["newproduct"])

    if name in session["products"]:
        return render_template("admin/addproduct.html", shopname=envs.SHOPNAME, admin=session["admin"], form=form, add_product_error="A product with this name already exists", product=session["newproduct"])

    product = Product(name=name, category=category, subcategory=subcategory, unit=unit, price=price, stock=stock, display=display, info=info, imageUrl=None)
    db.session.add(product)
    db.session.commit()
    p = Product.query.filter_by(name=name).first()

    url = add_image(form, str(p.id))

    if url == None:
        db.session.delete(p)
        db.session.commit()
        return render_template("admin/addproduct.html", shopname=envs.SHOPNAME, admin=session["admin"], form=form, add_product_error="Invalid/Missing Image", product=session["newproduct"])
    else:
        p.imageUrl = url
        db.session.commit()
        session["products"][name] = {
            "id": p.id,
            "name": name,
            "category": category,
            "subcategory": subcategory,
            "unit": unit,
            "price": price,
            "stock": stock,
            "url": url,
            "info": info,
            "display": display,
            "tags": None
        }
        if category not in session["categories"]:
            session["categories"].append(category)
        session["newproduct"] = session["products"][name]
    
    return redirect(url_for("admin_add_product"))


def add_image(form, name):
    """ push image in s3 bucket """
    s3_client = boto3.client('s3')
    prefix = "product-images/"
    if form.validate_on_submit():
        image_bytes = util.resize_image(form.photo.data, (500, 500))
        if image_bytes:
            key = prefix + name + '.png'
            s3_client.put_object(ACL='public-read', Bucket=envs.photo_bucket, Key=key, Body=image_bytes, ContentType='image/png')
            url = envs.s3_BUCKET_URL + key
            return url
        else:
            return None
    else:
        return None


@app.route("/admin/<string:name>/changeimage", methods=["POST", "GET"])
def admin_change_product_image(name):
    if session.get("customer") != None:
        return redirect(url_for('homepage'))
    if not session.get("admin"):
        return redirect(url_for('admin_login'))    
    
    get_products()
    if name not in session["products"]:
        return redirect("/admin")
    
    form = PhotoForm()    
    if request.method == "GET":
        return render_template("admin/changeimage.html", shopname=envs.SHOPNAME, product=session["products"][name], form=form, admin=session["admin"])
    
    p = Product.query.filter_by(name=name).first()
    if p == None:
        return redirect(url_for('admin_products'))
    #change image
    url = remove_and_add_image(form, str(p.id))
    if not url:
        return render_template("admin/changeimage.html", shopname=envs.SHOPNAME, product=session["products"][name], form=form, admin=session["admin"], change_image_error="Invalid/Missing Image")
    
    return redirect(url_for('admin_products'))


def remove_and_add_image(form, name):
    """" delete existing image and add a new image """
    s3_client = boto3.client('s3')
    prefix = "product-images/"
    if form.validate_on_submit():
        image_bytes = util.resize_image(form.photo.data, (500, 500))
        if image_bytes:
            key = prefix + name + '.png'
            s3_client.delete_object(Bucket=envs.photo_bucket, Key=key)
            s3_client.put_object(ACL='public-read', Bucket=envs.photo_bucket, Key=key, Body=image_bytes, ContentType='image/png')            
            return True
        else:
            return False
    else:
        return False


@app.route("/admin/<string:name>/modify", methods=["POST", "GET"])
def admin_modify_product(name):
    #edit product info
    if session.get("customer") != None:
        return redirect(url_for('homepage'))
    if not session.get("admin"):
        return redirect(url_for('admin_login'))    

    get_products()
    p = Product.query.filter_by(name=name).first()
    if p == None:
        return redirect("/admin")
    
    if request.method == "GET":
        return render_template("admin/editproduct.html", shopname=envs.SHOPNAME, product=session["products"][name], admin=session["admin"])
    
    new_name = request.form.get("name")
    category = request.form.get("category")
    subcategory = request.form.get("subcategory")
    unit = request.form.get("unit")
    price = request.form.get("price")
    stock = request.form.get("stock")
    display = request.form.get("display")
    info = request.form.get("info")

    if not new_name or not category or not unit or not price or not stock or not display:
        return render_template("admin/editproduct.html", shopname=envs.SHOPNAME, product=session["products"][name], admin=session["admin"], edit_product_error="fields marked with * can't be blank")

    if display == "True":
        display = True
    else:
        display = False
    
    if info:
        info = info.strip()
    else:
        info = None

    new_name = new_name.strip().title()
    category = category.strip().title()
    if subcategory:
        subcategory = subcategory.strip().title()
    else:
        subcategory = None
    unit = unit.strip().title()

    try:
        price = float(price)
        stock = float(stock)
    except:
        return render_template("admin/editproduct.html", shopname=envs.SHOPNAME, product=session["products"][name], admin=session["admin"], edit_product_error="price/stock value should be a number")

    if stock < 0 or price < 0:
        return render_template("admin/editproduct.html", shopname=envs.SHOPNAME, product=session["products"][name], admin=session["admin"], edit_product_error="stock and/or price can't be negative")

    if name != new_name:
        product = Product.query.filter_by(name=new_name).first()
        if product != None:
            return render_template("admin/editproduct.html", shopname=envs.SHOPNAME, product=session["products"][name], admin=session["admin"], edit_product_error="a product with this name already exists")

    p.name = new_name
    p.category = category
    p.subcategory = subcategory
    p.unit = unit
    p.price = price
    p.stock = stock
    p.info = info
    p.display = display
    db.session.commit()

    if category not in session["categories"]:
        session["categories"].append(category)

    tags = session["products"][name]["tags"]
    del session["products"][name]
    session["products"][new_name] = {
        "id": p.id,
        "name": new_name,
        "category": category,
        "subcategory": subcategory,
        "unit": unit,
        "price": price,
        "stock": stock,
        "url": p.imageUrl,
        "info": info,
        "display": display,
        "tags": tags
    }

    return redirect(url_for('admin_products'))


@app.route("/getinfo/<name>")
def getProductInfo(name):
    #ajax query to display product info
    if session.get("customer") != None:
        return jsonify({"success": False})
    if not session.get("admin"):
        return jsonify({"success": False})    
    
    if name not in session["products"]:
        return jsonify({"success": False})

    return jsonify({"success": True, "data": session["products"][name]})


def refresh():
    if session.get("products") != None:
        session["products"].clear()
        session["products"] = None
        session["categories"].clear()
    get_products()
    return
    

@app.route("/refresh")
def refresh_products():
    #refresh session["products"]
    if session.get("customer") != None:
        return redirect(url_for('homepage'))
    if not session.get("admin"):
        return redirect(url_for('admin_login'))
    refresh()
    return redirect(url_for('admin_products'))


@app.route("/admin/search", methods=["POST"])
def admin_search():
    if session.get("customer") != None:
        return redirect(url_for('homepage'))
    if not session.get("admin"):
        return redirect(url_for('admin_login'))    

    keyword = request.form.get("keyword")
    if not keyword:
        return render_template("admin/search.html", shopname=envs.SHOPNAME, admin=session["admin"], message="Type Something")
    
    keyword = keyword.strip().lower()
    refresh()
    results = []
    for key, value in session["products"].items():
        if value["tags"] == None:   #if there are no tags associated with this product
            if keyword in key.lower():
                results.append(value)
        else:
            if keyword in key.lower() or keyword in value["tags"]:
                results.append(value)


    return render_template("admin/search.html", shopname=envs.SHOPNAME, admin=session["admin"], results=results, keyword=keyword)


@app.route("/admin/newproducts")
def newproducts():
    #ajax request
    #this return a boolean
    #if there is any products with no tags associated with it
    #then it returns true
    #If all products have tags associated then it returns false
    if session.get("customer") != None:
        return jsonify({"success": False})
    if not session.get("admin"):
        return jsonify({"success": False})
    
    for value in session["products"].values():
        if value["tags"] == None:
            return jsonify({"success": True})
    
    return jsonify({"success": False})


def get_admin_orders():
    allorders = []
    orders = Order.query.order_by(Order.order_time.desc()).all()
    for order in orders:
        products = []
        transactions = order.transactions
        for t in transactions:
            p = Product.query.get(t.product_id)
            tr = {"name": p.name, "price": p.price, "unit": p.unit, "qty": t.qty, "amount": t.amount}
            products.append(tr)
        address = Address.query.get(order.addressID)
        o = {"order": order, "transactions": products, "address": address}
        allorders.append(o)

    return allorders


@app.route("/admin/orders")
def admin_orders():
    if session.get("customer") != None:
        return redirect(url_for('homepage'))
    if not session.get("admin"):
        return redirect(url_for('admin_login'))    

    orders = get_admin_orders()
    countO = Order.query.filter_by(status="OPEN").count()
    countCC = Order.query.filter_by(status="FOR CANCELLATION").count()

    return render_template("admin/orders.html", shopname=envs.SHOPNAME, admin=session["admin"], orders=orders, countO=countO, countCC=countCC)


@app.route("/admin/cancelorder/<int:orderid>")
def admin_cancel_order(orderid):
    if session.get("customer") != None:
        return jsonify({"success": False, "message": "Invalid Request"})
    if not session.get("admin"):
        return jsonify({"success": False, "message": "Invalid Request"})

    try:
        oid = int(orderid)
    except:
        return jsonify({"success": False, "message": "Invalid Request"})

    order = Order.query.get(oid)
    if order == None:
        return jsonify({"success": False, "message": "Invalid Request"})

    if order.status != "FOR CANCELLATION":
        return jsonify({"success": False, "message": "Invalid Request"})

    get_products()
    
    cancellation_time = datetime.now()
    order.status = "CANCELLED"
    order.prefered_time = None
    order.delivery_time = None
    order.cancellation_time = cancellation_time
    trs = order.transactions
    for tr in trs:
        p = Product.query.get(tr.product_id)
        p.stock += tr.qty
        session["products"][p.name]["stock"] = p.stock

    db.session.commit()
    socketio.emit("order cancelled", {"orderid": order.id, "username": order.username}, broadcast=False)
    return jsonify({"success": True, "cancellation_time": cancellation_time, "status": "CANCELLED"})


@app.route("/admin/closeorder/<int:orderid>")
def admin_close_order(orderid):
    if session.get("customer") != None:
        return jsonify({"success": False, "message": "Invalid Request"})
    if not session.get("admin"):
        return jsonify({"success": False, "message": "Invalid Request"})

    try:
        oid = int(orderid)
    except:
        return jsonify({"success": False, "message": "Invalid Request"})

    order = Order.query.get(oid)
    if order == None:
        return jsonify({"success": False, "message": "Invalid Request"})

    if order.status != "OPEN":
        return jsonify({"success": False, "message": "Invalid Request"})

    delivery_time = datetime.now()
    order.status = "CLOSED"
    order.delivery_time = delivery_time

    db.session.commit()
    socketio.emit("order closed", {"orderid": order.id, "username": order.username}, broadcast=False)
    return jsonify({"success": True, "delivery_time": delivery_time, "status": "CLOSED"})


@app.route("/admin/login", methods=["POST", "GET"])
def admin_login():
    if session.get("customer") != None:
        return redirect(url_for('homepage'))
    if session.get("admin"):
        return redirect(url_for('admin'))

    if request.method == "GET":
        return render_template("admin/login.html", shopname=envs.SHOPNAME)

    username = request.form.get("username")
    password = request.form.get("password")
    
    if not username or not password:
        return render_template("admin/login.html", shopname=envs.SHOPNAME, login_error="Enter Username and Password")
    
    if username == envs.ADMIN_USERNAME and password == envs.ADMIN_PASSWORD:
        session["admin"] = True
        session.permanent = True
        return redirect(url_for('admin'))
    else:
        return render_template("admin/login.html", shopname=envs.SHOPNAME, login_error="Invalid Username and/or Password")


@app.route("/admin/logout")
def admin_logout():
    if session.get("customer") != None:
        return redirect(url_for('homepage'))
    session.clear()
    return redirect(url_for('admin_login'))


def fetch_products():
    PRODUCTS = {}
    categories = []
    products = Product.query.filter_by(display=True).order_by(Product.name).all()
    for p in products:
        PRODUCTS[p.name] = {
            "id": p.id,
            "name": p.name,
            "category": p.category,
            "subcategory": p.subcategory,
            "unit": p.unit,
            "price": p.price,
            "stock": p.stock,
            "url": p.imageUrl,
            "display": p.display,
            "info": p.info,
            "tags": []
        }
        tags = Tags.query.filter_by(product_id=p.id).first()
        if tags != None:
            if tags.tag1:
                PRODUCTS[p.name]["tags"].append(tags.tag1)
            if tags.tag2:
                PRODUCTS[p.name]["tags"].append(tags.tag2)
            if tags.tag3:
                PRODUCTS[p.name]["tags"].append(tags.tag3)
            if tags.tag4:
                PRODUCTS[p.name]["tags"].append(tags.tag4)
            if tags.tag5:
                PRODUCTS[p.name]["tags"].append(tags.tag5)

        if p.category not in categories:
            categories.append(p.category)
    
    return {"products": PRODUCTS, "categories": categories}


def load_cart(username):
    session["cart"] = {}
    session["totalprice"] = 0
    transactions = Transaction.query.filter_by(status="INCART").filter_by(username=username).all()
    for t in transactions:
        p = Product.query.get(t.product_id)
        session["cart"][p.name] = {
            "name": p.name,
            "price": p.price,
            "unit": p.unit,
            "qty": t.qty,
            "amount": t.amount
        }
        session["totalprice"] += t.amount
    return


@app.route("/", methods=["POST", "GET"])
def homepage():
    if request.method == "GET":
        if session.get("admin"):
            return redirect(url_for('admin'))
        if session.get("customer") == None:
            return redirect(url_for('login'))

        if session.get("cart") == None:
            load_cart(session["customer"])

        if session.get("context") != None:
            session["context"].clear()
            session["context"] = None
        session["context"] = fetch_products()

        return render_template(
            "customers/homepage.html",
            shopname=envs.SHOPNAME,
            customer=session["customer"],
            categories=session["context"]["categories"],
            cart=session["cart"],
            amount=session["totalprice"]
        )
    else:
        #lazy loading
        #only 14 products are displayed at a time
        #new products are added when -
        #window.innerHeight + window.scrollY >= document.body.offsetHeight
        #refer to static/customers/productshome.js
        if session.get("admin"):
            return jsonify({"success": False})
        if session.get("customer") == None:
            return jsonify({"success": False})
            
        if session.get("context") == None:
            session["context"] = fetch_products()

        start = request.form.get("start")
        end = request.form.get("end")

        if not start or not end:
            return jsonify({"success": False})

        try:
            start = int(start)
            end = int(end)
        except:
            return jsonify({"success": False})
        
        l = len(session["context"]["products"])
        if end > l:
            end = l

        p = dict(itertools.islice(session["context"]["products"].items(), start, end))
        plist = list(p.values())
        return jsonify({"success": True, "products": plist})

    
@app.route("/search", methods=["POST"])
def search():
    if session.get("admin"):
        return redirect(url_for('admin'))
    if session.get("customer") == None:
        return redirect(url_for('login'))
    
    name = request.form.get("keyword")
    if not name:
        return render_template("customers/search.html", shopname=envs.SHOPNAME, customer=session["customer"], search_error="enter a keyword", keyword=None)
    
    if session.get("context") == None:
        session["context"] = fetch_products()
    
    result = []
    
    for pname, product in session["context"]["products"].items():
        if name.lower() in pname.lower() or name.lower() in product["tags"]:
            result.append(product)
    if result == []:
        return render_template("customers/search.html", shopname=envs.SHOPNAME, customer=session["customer"], keyword=name, search_error="Sorry! We couldn't find anything.")
        

    return render_template("customers/search.html", shopname=envs.SHOPNAME, customer=session["customer"], keyword=name, result=result)


@app.route("/ifcart")
def ifcart():
    #ajax request
    # if cart is empty then it returns false
    # and cart div is hidden
    # else cart div is displayed
    if session.get("admin"):
        return jsonify({"success": False})
    if session.get("customer") == None:
        return jsonify({"success": False})
    
    if session.get("cart") == None or session["cart"] == {}:
        return jsonify({"success": False})
    
    return jsonify({"success": True})


@app.route("/add2cart/<pid>/<qty>")
def add2cart(pid, qty):
    if session.get("admin"):
        return jsonify({"success": False, "message": "Invalid Request"})
    if session.get("customer") == None:
        return jsonify({"success": False, "message": "Invalid Request"})
    
    try:
        pid = int(pid)
        qty = float(qty)
    except:
        return jsonify({"success": False, "message": "Invalid Request"})

    p = Product.query.get(pid)
    if p == None:
        return jsonify({"success": False, "message": "Product Does Not Exist"})

    if p.stock <= 0:
        return jsonify({"success": False, "message": f"{p.name} is out of Stock."})
    elif p.stock < qty:
        return jsonify({"success": False, "message": f"Only {p.stock} {p.unit}(s) of {p.name}(s) is/are available."})

    if session.get("cart") == None:
        load_cart(session["customer"])

    if p.name in session["cart"]:
        #if product is already in cart then cart is updated
        QTY = session["cart"][p.name]["qty"] + qty
        if p.stock < QTY:
            # if new quantity is not available then customer is informed
            return jsonify({"success": False, "message": f"Only {p.stock} {p.unit}(s) of {p.name}(s) is/are available."})
        session["cart"][p.name].clear()
        session["cart"][p.name] = {"name": p.name, "price": p.price, "unit": p.unit, "qty": QTY, "amount": ((p.price)*(QTY))}
        session["totalprice"] = session["totalprice"] + ((p.price)*qty)
        amt = ((p.price)*(QTY))
        t = Transaction.query.filter_by(product_id=p.id).filter_by(status="INCART").filter_by(username=session["customer"]).first()
        t.qty = QTY
        t.amount = amt
    else:
        session["cart"][p.name] = {"name": p.name, "price": p.price, "unit": p.unit, "qty": qty, "amount": ((p.price)*qty)}
        session["totalprice"] = session["totalprice"] + ((p.price)*qty)
        amt = ((p.price)*(qty))
        t = Transaction(username=session["customer"], product_id=p.id, qty=qty, amount=amt)
        db.session.add(t)

    db.session.commit()

    return jsonify({"success": True, "cart": session["cart"], "amount": session["totalprice"]})


@app.route("/cart/remove/<name>")
def removeFromCart(name):
    if session.get("admin"):
        return jsonify({"success": False, "message": "Invalid Request"})
    if session.get("customer") == None:
        return jsonify({"success": False, "message": "Invalid Request"})

    if session.get("cart") == None:
        return jsonify({"success": False, "message": "Invalid Request"})
    
    if name not in session["cart"]:
        return jsonify({"success": False, "message": "Invalid Request"})

    session["totalprice"] = session["totalprice"] - session["cart"][name]["amount"]
    del session["cart"][name]

    if session["totalprice"] == 0 and session["cart"] == {}:
        session["cart"] = None

    p = Product.query.filter_by(name=name).first()
    t = Transaction.query.filter_by(product_id=p.id).filter_by(status="INCART").filter_by(username=session["customer"]).first()
    db.session.delete(t)
    db.session.commit()

    return jsonify({"success": True, "amount": session["totalprice"]})


@app.route("/erasecart")
def erasecart():
    #clear cart and delete all items
    if session.get("admin"):
        return jsonify({"success": False, "message": "Invalid Request"})
    if session.get("customer") == None:
        return jsonify({"success": False, "message": "Invalid Request"})

    if session.get("cart") == None:
        return jsonify({"success": False, "message": "Invalid Request"})

    session["cart"].clear()
    session["cart"] = None
    session["totalprice"] = 0

    transactions = Transaction.query.filter_by(status="INCART").filter_by(username=session["customer"]).all()
    for t in transactions:
        db.session.delete(t)

    db.session.commit()

    return jsonify({"success": True})


@app.route("/buy", methods=["POST", "GET"])
def placeorder():
    # confirm order and checkout
    if request.method == "GET":
        if session.get("admin"):
            return redirect(url_for('admin'))
        if session.get("customer") == None:
            return redirect(url_for('login'))
    
        if session.get("cart") == None or session["cart"] == {}:
            return redirect(url_for('homepage'))

        user = User.query.filter_by(username=session["customer"]).first()
        if user == None:
            return redirect(url_for('login'))
        
        addresses = user.addresses
        if len(addresses) == 0:
            return redirect(url_for('address'))

        cart = session["cart"].copy()
        message = []
        #re-check cart items for availability
        for key, value in cart.items():
            p = Product.query.filter_by(name=key).first()
            if p.stock <= 0:
                # if some product is out of stock then it is removed from cart
                # and its amount is deducted from total amount
                session["totalprice"] -= session["cart"][p.name]["amount"]
                del session["cart"][p.name]
                tr = Transaction.query.filter_by(status="INCART").filter_by(username=session["customer"]).filter_by(product_id=p.id).first()                
                db.session.delete(tr)
                message.append(f"{p.name} is out of Stock.")
            elif p.stock < value["qty"]:
                # if the product is in stock but the quantity in cart is now more than the stock value then
                # the difference in quantity is deducted from cart quantity.
                diff = value["qty"] - p.stock
                session["totalprice"] -= (diff*(p.price))
                session["cart"][p.name]["qty"] = p.stock
                session["cart"][p.name]["amount"] = ((p.stock)*(p.price))
                tr = Transaction.query.filter_by(status="INCART").filter_by(username=session["customer"]).filter_by(product_id=p.id).first()
                tr.qty = p.stock
                tr.amount = ((p.stock)*(p.price))
                message.append(f"Only {p.stock} {p.unit}(s) of {p.name}(s) is/are available.")
        #update cart items after re-checking for stock availability is rendered
        db.session.commit()
        return render_template("customers/buy.html", shopname=envs.SHOPNAME, customer=session["customer"], cart=session["cart"], amount=session["totalprice"], addresses=addresses, messages=message)

    else:# ajax post request
        if session.get("admin"):
            return jsonify({"success": False, "message": "Invalid Request"})
        if session.get("customer") == None:
            return jsonify({"success": False, "message": "Invalid Request"})
    
        if session.get("cart") == None or session["cart"] == {}:
            return jsonify({"success": False, "message": "Invalid Request"})

        address = request.form.get("address")
        time = request.form.get("time")

        if not time:
            time = None

        if not address:
            return jsonify({"success": False, "message": "Select a Delivery Address"})

        try:
            address = int(address)
        except:
            return jsonify({"success": False, "message": "Invalid Request"})
        
        while True:
            code = random.randint(100000, 9999999)
            o = Order.query.filter_by(code=code).first()
            if o == None:
                break

        order_time = datetime.now()
        o = Order(
            username=session["customer"],
            addressID=address,
            amount=session["totalprice"],
            order_time=order_time,
            prefered_time=time,
            code=code
        )
        db.session.add(o)

        tr = Transaction.query.filter_by(status="INCART").filter_by(username=session["customer"]).all()
        for t in tr:
            p = Product.query.get(t.product_id)
            p.stock -= t.qty
            t.status = "ORDERED"
            t.code = code
        
        db.session.commit()

        session["cart"].clear()
        session["cart"] = None
        session["totalprice"] = 0
        #this emit request sends code to administrator hearing at
        # static/admin/orders.js and static/admin/homepage.js
        socketio.emit("new order", {"code": code}, broadcast=False)
        return jsonify({"success": True, "message": code})


@app.route("/address", methods=["POST", "GET"])
def address():
    #add a delivery address
    if session.get("admin"):
        return redirect(url_for('admin'))
    if session.get("customer") == None:
        return redirect(url_for('login'))

    if request.method == "GET":
        return render_template("customers/address.html", shopname=envs.SHOPNAME, customer=session["customer"])

    name = request.form.get("name")
    mobile = request.form.get("mobile")
    address = request.form.get("address")
    city = request.form.get("city")
    state = request.form.get("state")
    pincode = request.form.get("pincode")
    country = request.form.get("country")

    if not name or not mobile or not address or not city or not state or not pincode or not country:
        return render_template("customers/address.html", shopname=envs.SHOPNAME, customer=session["customer"], address_form_error="fill in all fields marked with *")

    name = name.strip().title()
    mobile = mobile.strip()
    address = address.strip().title()
    city = city.strip().title()
    state = state.strip().title()
    pincode = pincode.strip()
    country = country.strip().title()

    a = Address(username=session["customer"], name=name, mobile=mobile, address=address, city=city, state=state, pincode=pincode, country=country)
    db.session.add(a)
    db.session.commit()
    return redirect("/buy")


def get_orders(username):
    allorders = []
    orders = Order.query.filter_by(username=username).order_by(Order.order_time.desc()).all()
    for order in orders:
        products = []
        transactions = order.transactions
        for t in transactions:
            p = Product.query.get(t.product_id)
            tr = {"name": p.name, "price": p.price, "unit": p.unit, "qty": t.qty, "amount": t.amount}
            products.append(tr)
        address = Address.query.get(order.addressID)
        o = {"order": order, "transactions": products, "address": address}
        allorders.append(o)

    return allorders


@app.route("/orders")
def orders():
    if session.get("admin"):
        return redirect(url_for('admin'))
    if session.get("customer") == None:
        return redirect(url_for('login'))
    #all orders and count of closed and cancelled orders
    orders = get_orders(session["customer"])
    countCL = Order.query.filter_by(status="CLOSED").filter_by(username=session["customer"]).count()
    countCN = Order.query.filter_by(status="CANCELLED").filter_by(username=session["customer"]).count()
    return render_template("customers/orders.html", shopname=envs.SHOPNAME, customer=session["customer"], orders=orders, countCL=countCL, countCN=countCN)


@app.route("/cancel/order/<int:orderid>")
def cancel(orderid):
    if session.get("admin"):
        return jsonify({"success": False, "message": "Invalid Request"})

    if session.get("customer") == None:
        return jsonify({"success": False, "message": "Invalid Request"})

    try:
        orderid = int(orderid)
    except:
        return jsonify({"success": False, "message": "Invalid Request"})

    o = Order.query.get(orderid)
    if o == None:
        return jsonify({"success": False, "message": "Invalid Request"})

    if o.status != "OPEN":
        return jsonify({"success": False, "message": "Invalid Request"})

    if o.username != session["customer"]:
        return jsonify({"success": False, "message": "Invalid Request"})

    o.status = "FOR CANCELLATION"
    o.prefered_time = None
    db.session.commit()
    #this emit request sends code to administrator hearing at
    # static/admin/orders.js and static/admin/homepage.js
    socketio.emit("order cancellation", {"code": o.code}, broadcast=False)
    return jsonify({"success": True, "message": "FOR CANCELLATION"})


@app.route("/productInfo/<name>")
def productInfo(name):
    #ajax request
    if session.get("admin"):
        return jsonify({"success": False, "message": "Invalid Request"})

    if session.get("customer") == None:
        return jsonify({"success": False, "message": "Invalid Request"})

    p = Product.query.filter_by(name=name).first()
    if p == None:
        return jsonify({"success": False, "message": "Product Does Not Exist"})
    
    #displays product info on customer homepage
    return jsonify({"success": True, "message": p.info})


@app.route("/getusername")
def getusername():
    if session.get("admin"):
        return jsonify({"success": False})

    # when administrators mark some order as dispatched or process order cancellation request
    # this ajax request is used to verify socketio emits
    # statis/orders.js line 7 and 19

    if session.get("customer") == None:
        return jsonify({"success": False})
    else:
        return jsonify({"success": True, "username": session["customer"]})


@app.route("/login", methods=["POST", "GET"])
def login():
    if session.get("admin"):
        return redirect(url_for('admin'))
    if session.get("customer") != None:
        return redirect(url_for('homepage'))

    if request.method == "GET":
        return render_template("customers/auth/login.html", shopname=envs.SHOPNAME, login=True)
    
    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return render_template("customers/auth/login.html", shopname=envs.SHOPNAME, login=True, login_error="enter username and password")
    
    username = username.strip()
    user = User.query.filter_by(username=username).first()
    if user == None:
        return render_template("customers/auth/login.html", shopname=envs.SHOPNAME, login=True, login_error="Invalid Credentials")
    
    if check_password_hash(user.password, password):
        session["customer"] = username
        session.permanent = True
        return redirect(url_for('homepage'))
    
    return render_template("customers/auth/login.html", shopname=envs.SHOPNAME, login=True, login_error="Invalid Credentials")


@app.route("/logout")
def logout():
    if session.get("admin"):
        return redirect(url_for('admin'))
    session.clear()
    return redirect(url_for('login'))


@app.route("/register", methods=["POST", "GET"])
def register():
    if session.get("admin"):
        return redirect(url_for('admin'))

    if session.get("customer") != None:
        return redirect(url_for('homepage'))
    
    if request.method == "GET":
        return render_template("customers/auth/register.html", shopname=envs.SHOPNAME, register=True)

    username = request.form.get("username")
    email = request.form.get("email")
    password1 = request.form.get("password1")
    password2 = request.form.get("password2")

    if not username or not email or not password1 or not password2:
        return render_template("customers/auth/register.html", shopname=envs.SHOPNAME, register_error="fill in all fields", register=True)

    if username == envs.ADMIN_USERNAME:
        return render_template("customers/auth/register.html", shopname=envs.SHOPNAME, register_error="Username already taken. Select a different Username", register=True)

    if not util.validate_username(username):
        return render_template("customers/auth/register.html", shopname=envs.SHOPNAME, register_error="Invalid Username", register=True)
    
    if not util.validate_password(password1):
        return render_template("customers/auth/register.html", shopname=envs.SHOPNAME, register_error="Type a Strong Password", register=True)

    if not util.validate_email(email):
        return render_template("customers/auth/register.html", shopname=envs.SHOPNAME, register_error="Invalid Email Address", register=True)

    if password1 != password2:
        return render_template("customers/auth/register.html", shopname=envs.SHOPNAME, register_error="passwords don't match", register=True)
    
    user = User.query.filter_by(email=email).first()
    if user != None:
        return render_template("customers/auth/register.html", shopname=envs.SHOPNAME, register_error="This email is associated with another account.", register=True)

    user = User.query.filter_by(username=username).first()
    if user != None:
        return render_template("customers/auth/register.html", shopname=envs.SHOPNAME, register_error="Username already taken. Select a different Username", register=True)
    
    password = generate_password_hash(password1)
    username = username.strip()
    code = str(random.randint(100000, 999999))
    session["userinfo"] = {"email": email, "password": password, "username": username, "code": code}
    
    message1 = f"<h1 style='text-align: center;'>{envs.SHOPNAME}</h1>"
    message2 = f"<h2 style='text-align: center;'>{code}</h2>"
    message3 = "<h3 style='text-align: center;'>Verify Your Email Address</h3>"
    m = message1 + message2 + message3
    util.sendmail(email, "Email Verification", m)
    return redirect("/verification")


@app.route("/resend")
def resendverificationcode():
    if session.get("admin"):
        return redirect(url_for('admin'))

    if session.get("customer") != None:
        return redirect(url_for('homepage'))

    if session.get("userinfo") == None:
        return redirect(url_for('homepage'))

    code = str(random.randint(100000, 999999))
    session["userinfo"]["code"] = code    
    message1 = f"<h1 style='text-align: center;'>{envs.SHOPNAME}</h1>"
    message2 = f"<h2 style='text-align: center;'>{code}</h2>"
    message3 = "<h3 style='text-align: center;'>Verify Your Email Address</h3>"
    m = message1 + message2 + message3
    util.sendmail(session["userinfo"]["email"], "Email Verification", m)
    return redirect("/verification")


@app.route("/verification", methods=["POST", "GET"])
def verification():
    if session.get("admin"):
        return redirect(url_for('admin'))

    if session.get("customer") != None:
        return redirect(url_for('homepage'))

    if session.get("userinfo") == None:
        return redirect(url_for('homepage'))
        
    if request.method == "GET":
        return render_template("customers/auth/verification.html", shopname=envs.SHOPNAME, email=session["userinfo"]["email"], register=True)
    
    code = request.form.get("code")
    if not code:
        return render_template("customers/auth/verification.html", shopname=envs.SHOPNAME, email=session["userinfo"]["email"], register=True, verification_code_error="enter verification code")
    
    if code != session["userinfo"]["code"]:
        return render_template("customers/auth/verification.html", shopname=envs.SHOPNAME, email=session["userinfo"]["email"], register=True, verification_code_error="incorrect verification code")

    user = User(email=session["userinfo"]["email"], password=session["userinfo"]["password"], username=session["userinfo"]["username"])
    db.session.add(user)
    db.session.commit()

    message1 = f"<h1 style='text-align: center;'>{envs.SHOPNAME}</h1>"
    message2 = "<h2 style='text-align: center;'>Registration Successful</h2>"
    m = message1 + message2
    util.sendmail(session["userinfo"]["email"], "Confirmation", m)

    session["userinfo"].clear()
    session["userinfo"] = None

    return redirect("/login")


@app.route("/changepassword", methods=["POST", "GET"])
def changepassword():
    if session.get("admin"):
        return redirect(url_for('admin'))

    if session.get("customer") == None:
        return redirect(url_for('login'))
    
    if request.method == "GET":
        return render_template("customers/changepassword.html", shopname=envs.SHOPNAME, customer=session["customer"])

    oldpassword = request.form.get("oldpassword")
    password1 = request.form.get("password1")
    password2 = request.form.get("password2")

    if not oldpassword or not password1 or not password2:
        return render_template("customers/changepassword.html", shopname=envs.SHOPNAME, customer=session["customer"], changepassword_error="fill in all details")
    
    if password2 != password1:
        return render_template("customers/changepassword.html", shopname=envs.SHOPNAME, customer=session["customer"], changepassword_error="New passwords don't match.")
    
    if not util.validate_password(password1):
        return render_template("customers/changepassword.html", shopname=envs.SHOPNAME, customer=session["customer"], changepassword_error="Please select a strong password.")

    user = User.query.filter_by(username=session["customer"]).first()
    if check_password_hash(user.password, oldpassword):
        password = generate_password_hash(password1)
        user.password = password
        db.session.commit()
        return redirect(url_for('homepage'))
    else:
        return render_template("customers/changepassword.html", shopname=envs.SHOPNAME, customer=session["customer"], changepassword_error="Current password is incorrect.")


@app.route("/forgotpassword", methods=["POST", "GET"])
def forgotpassword():
    if session.get("admin"):
        return redirect(url_for('admin'))

    if session.get("customer") != None:
        return redirect(url_for('homepage'))
    
    if request.method == "GET":
        return render_template("customers/auth/password.html", shopname=envs.SHOPNAME, fp=True)
    
    email = request.form.get("email")

    if not email:
        return render_template("customers/auth/password.html", shopname=envs.SHOPNAME, fp=True, fp_error="type your email address or username")

    user = User.query.filter_by(email=email).first()
    if user == None:
        user = User.query.filter_by(username=email).first()
        if user == None:
            return render_template("customers/auth/password.html", shopname=envs.SHOPNAME, fp=True, fp_error="Invalid Credentials")

    code = str(random.randint(100000, 999999))
    util.sendmail(user.email, "Verify Email Address", code)
    session["userinfo"] = {"user": user, "code": code}
    return redirect(url_for('recoverpassword'))

@app.route("/recoverpassword", methods=["POST", "GET"])
def recoverpassword():
    if session.get("admin"):
        return redirect(url_for('admin'))

    if session.get("customer") != None:
        return redirect(url_for('homepage'))
    
    if session.get("userinfo") == None:
        return redirect(url_for('homepage'))
    
    if request.method == "GET":
        return render_template("customers/auth/recoverpassword.html", shopname=envs.SHOPNAME, fp=True)
    
    code = request.form.get("code")
    if not code:
        return render_template("customers/auth/recoverpassword.html", shopname=envs.SHOPNAME, fp=True, fp_code_error="enter verification code")
    if code != session["userinfo"]["code"]:
        return render_template("customers/auth/recoverpassword.html", shopname=envs.SHOPNAME, fp=True, fp_code_error="incorrect code")
    
    return redirect(url_for('changeyourpassword'))


@app.route("/changeyourpassword", methods=["POST", "GET"])
def changeyourpassword():
    if session.get("admin"):
        return redirect(url_for('admin'))

    if session.get("customer") != None:
        return redirect(url_for('homepage'))
    
    if session.get("userinfo") == None:
        return redirect(url_for('homepage'))

    if request.method == "GET":
        return render_template("customers/auth/changeyourpassword.html", shopname=envs.SHOPNAME, fp=True)

    password1 = request.form.get("password1")
    password2 = request.form.get("password2")

    if not password1 or not password2:
        return render_template("customers/auth/changeyourpassword.html", shopname=envs.SHOPNAME, fp=True, changepassword_error="fill in all fields")
    
    if password2 != password1:
        return render_template("customers/auth/changeyourpassword.html", shopname=envs.SHOPNAME, fp=True, changepassword_error="passwords don't match")

    if not util.validate_password(password1):
        return render_template("customers/auth/changeyourpassword.html", shopname=envs.SHOPNAME, fp=True, changepassword_error="set a strong password")
    
    user = User.query.filter_by(username=session["userinfo"]["user"].username).first()
    if user == None:
        return redirect(url_for('login'))

    password = generate_password_hash(password1)
    user.password = password
    db.session.commit()

    session["userinfo"].clear()
    session["userinfo"] = None

    return redirect(url_for('login'))


@app.route("/resendcode")
def resendcode():
    if session.get("admin"):
        return redirect(url_for('admin'))

    if session.get("customer") != None:
        return redirect(url_for('homepage'))
    
    if session.get("userinfo") == None:
        return redirect(url_for('homepage'))

    code = str(random.randint(100000, 999999))
    util.sendmail(session["userinfo"]["user"].email, "Verify Email Address", code)
    session["userinfo"]["code"] = code

    return redirect(url_for('recoverpassword'))


@app.route("/contactus", methods=["POST", "GET"])
def contactus():
    if request.method == "GET":
        if session.get("admin"):
            return redirect(url_for('admin'))

        if session.get("customer") == None:
            return redirect(url_for('login'))
        return render_template("customers/contactus.html", shopname=envs.SHOPNAME, customer=session["customer"])
    else:
        if session.get("admin"):
            return jsonify({"success": False, "message": "Invalid Request"})

        if session.get("customer") == None:
            return jsonify({"success": False, "message": "Invalid Request"})

        name = request.form.get("name")
        subject = request.form.get("subject")
        message = request.form.get("message")

        if not name or not subject or not message:
            return jsonify({"success": False, "message": "Incomplete Details"})
        
        s = f'<Subject: {subject}> <Name: {name}> <Username: {session["customer"]}>'
        try:
            util.sendmail(envs.ADMIN_EMAIL_ADDRESS, s, message)
        except:
            return jsonify({"success": False, "message": "Something went wrong. Please try again after sometime."})

        return jsonify({"success": True})


# admin page - code for new-order/order-cancellation notification (websocket)
@app.route("/admin/orderdetails/<int:code>")
def orderdetails(code):
    if not session.get("admin"):
        return jsonify({"success": False, "message": "Invalid Request"})

    try:
        code = int(code)
    except:
        return jsonify({"success": False, "message": "Invalid Request"})
    
    order = Order.query.filter_by(code=code).first()
    if order == None:
        return jsonify({"success": False, "message": "Invalid Request"})


    transactions = order.transactions
    tr = []
    for t in transactions:
        p = Product.query.get(t.product_id)
        item = {"name": p.name, "price": p.price, "unit": p.unit, "qty": t.qty, "amount": t.amount}
        tr.append(item)

    if order.status == "OPEN":
        neworder = True
    else:
        neworder = False

    address = Address.query.get(order.addressID)
    response = {        
        "name": address.name,
        "address": address.address,
        "city": address.city,
        "state": address.state,
        "pincode": address.pincode,
        "country": address.country,
        "mobile": address.mobile,
        "status": order.status,
        "id": order.id,
        "transactions": tr,
        "username": order.username,
        "amount": order.amount,
        "order_time": order.order_time,
        "delivery_time": order.delivery_time,
        "cancellation_time": order.cancellation_time,
        "prefered_time": order.prefered_time,
        "code": code,
        "neworder": neworder
    }
    return jsonify({"success": True, "response": response})


# customer page - code for closed-order/cancelled-order notification (websocket)
@app.route("/orderdetails/<username>/<int:orderid>")
def order_details(username, orderid):
    if session.get("customer") == None:
        return jsonify({"success": False})
    elif session["customer"] != username:
        return jsonify({"success": False})
    
    try:
        oid = int(orderid)
    except:
        return jsonify({"success": False})

    order = Order.query.get(oid)
    if order == None:
        return jsonify({"success": False})

    if order.status != "CLOSED" and order.status != "CANCELLED":
        return jsonify({"success": False})

    transactions = order.transactions
    tr = []
    for t in transactions:
        p = Product.query.get(t.product_id)
        item = {"name": p.name, "price": p.price, "unit": p.unit, "qty": t.qty, "amount": t.amount}
        tr.append(item)

    address = Address.query.get(order.addressID)
    response = {        
        "name": address.name,
        "address": address.address,
        "city": address.city,
        "state": address.state,
        "pincode": address.pincode,
        "country": address.country,
        "mobile": address.mobile,
        "status": order.status,
        "id": order.id,
        "transactions": tr,
        "username": order.username,
        "amount": order.amount,
        "order_time": order.order_time,
        "delivery_time": order.delivery_time,
        "cancellation_time": order.cancellation_time,
        "prefered_time": order.prefered_time,
        "code": order.code
    }

    return jsonify({"success": True, "response": response})