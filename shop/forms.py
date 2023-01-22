from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, PasswordField, HiddenField,
                     IntegerField, TextAreaField)
from wtforms.validators import DataRequired, Email, Optional, NumberRange


##WTForm
class CartForm(FlaskForm):
    product_id = StringField("Blog Post Title", validators=[DataRequired()])
    product_name = StringField("Subtitle", validators=[Optional()])
    quantity = IntegerField("Quantity", validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField("Update")


class UserForm(FlaskForm):
    email = StringField("email", validators=[DataRequired(), Email()])
    password = PasswordField("password", validators=[DataRequired()])
    name = StringField("name", validators=[DataRequired()])
    submit = SubmitField("Submit")


class ContactForm(FlaskForm):
    email = StringField("email", validators=[DataRequired(), Email()])
    name = StringField("name", validators=[DataRequired()])
    message = TextAreaField("message", validators=[DataRequired()])
    submit = SubmitField("Submit")


class LoginForm(UserForm):
    name = HiddenField("name")