from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, TextAreaField, PasswordField, BooleanField, ValidationError, FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_ckeditor import CKEditorField


class ContactForm(FlaskForm):
    name           = StringField("Name:", validators=[DataRequired(), Length(max=100)])
    email          = EmailField("E-mail Address:", validators=[DataRequired(),Email(), Length(max=150)])
    message        = TextAreaField("Message: 500 characters or less", validators=[DataRequired(), Length(max=500)])
    send           = SubmitField("Send Message")
    
    
class UserForm(FlaskForm):
    name           = StringField("Name:", validators=[DataRequired(), Length(max=100)])
    username       = StringField("Username:", validators=[DataRequired(), Length(max=100)])
    email          = EmailField("E-mail Address:", validators=[DataRequired(),Email(), Length(max=150)])
    password_hash  = PasswordField('Password', validators=[DataRequired(), EqualTo('verify_pw', message='Passwords Must Match!')])
    verify_pw      = PasswordField('Verify Password', validators=[DataRequired()])
    submit         = SubmitField("Submit User")
    update         = SubmitField("Update Profile")
    delete         = SubmitField("Delete User")
    
class PostForm(FlaskForm):
    title          = StringField("Title",validators=[DataRequired()])
    content        = CKEditorField('Content', validators=[DataRequired()])
    author         = StringField("Author")
    slug           = StringField("Slug",validators=[DataRequired()])
    submit         = SubmitField("Submit")

class PasswordForm(FlaskForm):
    email          = EmailField("What's Your E-mail Address:", validators=[DataRequired(),Email(), Length(max=150)])
    password_hash  = PasswordField("What's Your Password", validators=[DataRequired()])
    submit         = SubmitField("Submit")   

class LoginForm(FlaskForm):
    username       = StringField("Username", validators=[DataRequired()])
    password       = PasswordField("Password", validators=[DataRequired()])
    login          = SubmitField("Login")

class SearchForm(FlaskForm):
    searched       = StringField("Searched", validators=[DataRequired()])
    submit        = SubmitField("Search") 
    

        
    