#assignment 2
#PROG38263
#Danyal Khan 991 389 587
#Mizanur Rahman 981388924

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Length, EqualTo, InputRequired, Email

class RegistrationForm(FlaskForm):
    firstname = StringField('First Name',        [ InputRequired(), Length(min=1, max=64) ])
    lastname  = StringField('Last Name',         [ InputRequired(), Length(min=1, max=64) ])
    email     = EmailField('Email Address',      [ InputRequired(), Email() ])
    password  = PasswordField('Password',        [ InputRequired(), Length(min=5, max=256)])        
    confirm   = PasswordField('Repeat Password', [ EqualTo('password', message="Passwords don't match") ])


class LoginForm(FlaskForm):
    email    = EmailField('Email Address',  [ InputRequired(), Email() ])
    password = PasswordField('Password',    [ InputRequired(), Length(min=5, max=256) ])
                                              
                                              
class EmailForm(FlaskForm):
    email = EmailField('Email Address', [ InputRequired(), Email() ])
    
class ResetPasswordForm(FlaskForm):
    password  = PasswordField('New Password',    [ InputRequired(), Length(min=5, max=256) ])
    confirm   = PasswordField('Repeat Password', [ EqualTo('password', message="Passwords don't match") ])
    
