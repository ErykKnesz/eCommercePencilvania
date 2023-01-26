from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, PasswordField, HiddenField,
                     IntegerField, TextAreaField, FloatField)
from wtforms.validators import (DataRequired, Email, Optional,
                                NumberRange, ValidationError)
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_uploads import UploadSet, IMAGES

images = UploadSet("images",
                   IMAGES,
                   default_dest=lambda app: app.config["UPLOADED_PHOTOS_DEST"])


class CartForm(FlaskForm):
    product_id = StringField("Blog Post Title", validators=[DataRequired()])
    product_name = StringField("Subtitle", validators=[Optional()])
    quantity = IntegerField("Quantity", validators=[DataRequired(),
                                                    NumberRange(min=1)])
    submit = SubmitField("Update")


class UserForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Submit")


class LoginForm(UserForm):
    name = HiddenField("Name")


def is_numeric(form, field):
    try:
        float(field.data)
    except ValueError:
        raise ValidationError(
            "Field must be of numeric type only! e.g. 1 or 1.50")


class ProductForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    image = FileField("Upload File",
                      validators=[FileRequired(),
                                  FileAllowed(images, 'Images only!')])
    price = FloatField("Price", validators=[DataRequired(),
                                            NumberRange(min=1), is_numeric])
    submit = SubmitField("Submit")


class AddressForm(FlaskForm):
    line_1 = TextAreaField("Line 1", validators=[Optional()])
    line_2 = TextAreaField("Line 2", validators=[Optional()])
    street = TextAreaField("Street", validators=[DataRequired()])
    city = StringField("City", validators=[DataRequired()])
    postcode = StringField("Postcode", validators=[DataRequired()])
    country = StringField("Country", validators=[DataRequired()])
    submit = SubmitField("Submit")
