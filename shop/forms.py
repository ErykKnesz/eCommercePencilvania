from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, HiddenField, IntegerField
from wtforms.validators import DataRequired, Email, Optional


##WTForm
class CartForm(FlaskForm):
    product_id = StringField("Blog Post Title", validators=[DataRequired()])
    product_name = StringField("Subtitle", validators=[Optional()])
    quantity = IntegerField("Quantity", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


class UserForm(FlaskForm):
    email = StringField("email", validators=[DataRequired(), Email()])
    password = PasswordField("password", validators=[DataRequired()])
    name = StringField("name", validators=[DataRequired()])
    submit = SubmitField("Submit")


class LoginForm(UserForm):
    name = HiddenField("name")