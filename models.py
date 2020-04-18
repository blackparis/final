import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)    
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False, unique=True)

class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    category = db.Column(db.String, nullable=False)
    info = db.Column(db.String, nullable=True)
    subcategory = db.Column(db.String, nullable=True)
    unit = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Float, nullable=False)
    display = db.Column(db.Boolean, nullable=False)
    imageUrl = db.Column(db.String, nullable=True)
    tags = db.relationship("Tags", lazy=True)
    transactions = db.relationship("Transaction", lazy=True)


class Tags(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    tag1 = db.Column(db.String, nullable=False)
    tag2 = db.Column(db.String, nullable=True)
    tag3 = db.Column(db.String, nullable=True)
    tag4 = db.Column(db.String, nullable=True)
    tag5 = db.Column(db.String, nullable=True)


class Address(db.Model):
    __tablename__ = "addresses"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, db.ForeignKey("users.username"), nullable=False)
    name = db.Column(db.String, nullable=False)
    mobile = db.Column(db.String, nullable=False)
    address1 = db.Column(db.String, nullable=False)
    address2 = db.Column(db.String, nullable=True)
    city = db.Column(db.String, nullable=False)
    state = db.Column(db.String, nullable=False)
    pincode = db.Column(db.String, nullable=False)
    country = db.Column(db.String, nullable=False)


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, db.ForeignKey("users.username"), nullable=False)
    addressID = db.Column(db.Integer, db.ForeignKey("addresses.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    order_time = db.Column(db.DateTime, nullable=False)
    prefered_time = db.Column(db.String, nullable=True)
    delivery_time = db.Column(db.DateTime, nullable=True)
    cancellation_time = db.Column(db.DateTime, nullable=True)
    code = db.Column(db.Integer, nullable=False, unique=True)
    status = db.Column(db.String, nullable=False, default="OPEN")
    transactions = db.relationship("Transaction", lazy=True)


class Transaction(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    qty = db.Column(db.Float, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String, nullable=False, default="INCART")
    code = db.Column(db.Integer, db.ForeignKey("orders.code"), nullable=True)