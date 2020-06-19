from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import Email, EqualTo, Length, DataRequired, ValidationError
import json

class RegisterForm(FlaskForm):
    first_name          = StringField("First Name", validators=[DataRequired(), Length(min=2, max=30)])
    last_name           = StringField("Last Name", validators=[DataRequired(), Length(min=2, max=30)])
    email               = StringField("Email", validators=[DataRequired(), Email()])
    password            = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=15)])
    confirm_password    = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password'), Length(min=6, max=15)])
    submit              = SubmitField("Register Now")

    def validate_email(self, email):
        with open('users.json') as read_file:
            users = json.load(read_file)
        for user in users:
            if user['email'] == email.data:
                raise ValidationError('Email is already in use')

class LoginForm(FlaskForm):
    email               = StringField("Email", validators=[DataRequired(), Email()])
    password            = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=15)])
    submit              = SubmitField("Login")

class AddNewsForm(FlaskForm):
    headline            = StringField("Headline", validators=[DataRequired(), Length(min=2, max=30)])
    category            = StringField("News Category", validators=[DataRequired(), Length(min=2, max=15)])
    author_name         = StringField("Author Name", validators=[DataRequired(), Length(min=2, max=50)])
    description         = TextAreaField("Description", validators=[DataRequired()])
    submit              = SubmitField("Add")
