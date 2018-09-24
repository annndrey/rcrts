#!/usr/bin/python
# -*- coding: utf-8 -*-

from passlib.apps import custom_app_context as pwd_context
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref, validates
from sqlalchemy import ForeignKey
from app import db
from flask_login import UserMixin

from sqlalchemy.orm import backref, validates


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(400))
    password_hash = db.Column(db.String(400))
    note = db.Column(db.Text(), nullable=True)
    is_confirmed = db.Column(db.Boolean, default=False)
    confirmed_on = db.Column(db.DateTime, default=False)
    registered_on = db.Column(db.DateTime, default=False)
    admin = db.Column(db.Boolean, default=False)
    subscriptions = db.relationship("Subscription", backref="user", cascade="all,delete")
    plan_id = db.Column(db.Integer, db.ForeignKey('tariff_plan.id'), nullable=False)
    subscr_left = db.Column(db.Integer, default=0, nullable=False)

    @validates('login')
    def validate_login(self, key, login):
        if len(login) > 1:
            assert '@' in login, 'Invalid email'
        return login

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)


class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    note = db.Column(db.Text())


class TariffPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(400))
    price = db.Column(db.Integer)
    description = db.Column(db.Text())
    note = db.Column(db.Text())
    users = db.relationship('User', backref='plan')
    subscr_num = db.Column(db.Integer, nullable=False, default=5)

