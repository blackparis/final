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
                "tags": []
            }

            tags = Tags.query.filter_by(product_id=p.id).first()
            if tags != None:
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


@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect(url_for('admin_login'))
    get_products()
    return render_template("admin/homepage.html", shopname=envs.SHOPNAME, admin=session["admin"])


@app.route("/admin/products")
def admin_products():
    if not session.get("admin"):
        return redirect(url_for('admin_login'))

    get_products()
    return render_template("admin/products.html", shopname=envs.SHOPNAME, admin=session["admin"], products=session["products"], categories=session["categories"])


@app.route("/admin/products/details")
def admin_products_details():
    if not session.get("admin"):
        return redirect(url_for('admin_login'))

    get_products()
    return render_template("admin/detailedproducts.html", shopname=envs.SHOPNAME, admin=session["admin"], products=session["products"], categories=session["categories"])


@app.route("/admin/<name>/tags/edit", methods=["POST", "GET"])
def admin_edit_tags(name):
    if not session.get("admin"):
        return redirect(url_for('admin_login'))
    
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
    t = []
    tag1 = tag1.strip()
    t.append(tag1)
    tag.tag1 = tag1

    if tag2:
        tag2 = tag2.strip()
        t.append(tag2)
        tag.tag2 = tag2
    else:
        tag.tag2 = None
    
    if tag3:
        tag3 = tag3.strip()
        t.append(tag3)
        tag.tag3 = tag3
    else:
        tag.tag3 = None

    if tag4:        
        tag4 = tag4.strip()
        t.append(tag4)
        tag.tag4 = tag4
    else:
        tag.tag4 = None

    if tag5:
        tag5 = tag5.strip()
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
    if not session.get("admin"):
        return redirect(url_for('admin_login'))
    
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
    tag1 = tag1.strip()
    t.append(tag1)

    if tag2:
        tag2 = tag2.strip()
        t.append(tag2)
    else:
        tag2 = None
    
    if tag3:
        tag3 = tag3.strip()
        t.append(tag3)
    else:
        tag3 = None

    if tag4:        
        tag4 = tag4.strip()
        t.append(tag4)
    else:
        tag4 = None

    if tag5:
        tag5 = tag5.strip()
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
    if not session.get("admin"):
        return redirect(url_for('admin_login'))
    
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
            "tags": []
        }
        if category not in session["categories"]:
            session["categories"].append(category)
        session["newproduct"] = session["products"][name]
    
    return redirect(url_for("admin_add_product"))


def add_image(form, name):
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

    url = remove_and_add_image(form, str(p.id))
    if not url:
        return render_template("admin/changeimage.html", shopname=envs.SHOPNAME, product=session["products"][name], form=form, admin=session["admin"], change_image_error="Invalid/Missing Image")
    
    return redirect(url_for('admin_products'))


def remove_and_add_image(form, name):
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
    if not session.get("admin"):
        return jsonify({"success": False})
    
    if name not in session["products"]:
        return jsonify({"success": False})

    return jsonify({"success": True, "data": session["products"][name]})


@app.route("/admin/login", methods=["POST", "GET"])
def admin_login():
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
    session.clear()
    return redirect(url_for('admin_login'))


@app.route("/")
def homepage():
    return "hello, world"


if __name__ == '__main__':
    socketio.run(app)