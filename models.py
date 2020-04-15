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

class Tags(db.Model):
    __tablename__ = "tags"
    id = id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    tag1 = db.Column(db.String, nullable=False)
    tag2 = db.Column(db.String, nullable=True)
    tag3 = db.Column(db.String, nullable=True)
    tag4 = db.Column(db.String, nullable=True)
    tag5 = db.Column(db.String, nullable=True)