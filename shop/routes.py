from functools import wraps

from flask import (render_template, redirect, url_for, flash, request,
                   abort, session)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
from sqlalchemy.exc import IntegrityError

from shop import app, db
from shop.models import User, Product
from shop.forms import UserForm, LoginForm, CartForm
from cart_serializer import cart_to_dict


login_manager = LoginManager()
login_manager.init_app(app)


def admin_only(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            if current_user.id == 1:
                return func(*args, **kwargs)
        except AttributeError:
            return abort(403)
    return inner


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(user_id)
    return user


@app.route('/register', methods=["GET", "POST"])
def register():
    form = UserForm()
    if request.method == "POST" and form.validate_on_submit():
        pass_hash = generate_password_hash(form.data["password"],
                                           method='pbkdf2:sha256',
                                           salt_length=8)
        try:
            user = User(
                email=form.data["email"],
                password=pass_hash,
                name=form.data["name"]
            )
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            flash('This email address is already used')
            return redirect(url_for('login'))
        return redirect(url_for("get_products"))
    return render_template("register.html", form=form)


@app.route('/login',  methods=["GET", "POST"])
def login():
    form = LoginForm()
    next_url = request.args.get('next')
    if request.method == "POST":
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.data['email']).first()
            if user:
                if check_password_hash(user.password, form.data["password"]):
                    login_user(user)
                    session['logged_in'] = True
                    session.permanent = True  # Use cookie to store session.
                    flash('You are now logged in.', 'success')
                    return redirect(next_url or url_for('get_products'))
                flash('Wrong password.')
                return redirect(url_for('login'))
            flash('Email address not found.')
            return redirect(url_for('login'))
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('get_products'))


@app.route('/')
def get_products():
    products = Product.query.all()
    form = CartForm()
    return render_template("shop.html", products=products, form=form)


@app.route('/cart/add/', methods=["POST"])
def add_to_cart():
    form = CartForm()
    if form.validate_on_submit():
        product_id = form.data["product_id"]
        product = db.session.query(Product).get(product_id)
        if session.get("cart") is None:
            session["cart"] = ""
        qty = form.data["quantity"]
        cart_contents = '''{
            "product_id": %d,
            "quantity": %d 
        }''' % (product.id, qty)
        print(cart_contents)
        session["cart"] += cart_contents + ";"
        cart_to_dict(session.get("cart"))
    return redirect(url_for("get_products"))


@app.route('/cart')
def get_cart():
    return render_template("cart.html")


@app.route("/product/<int:product_id>")
def show_product(product_id):
    product = Product.query.get(product_id)
    cart_form = ""
    return render_template("product.html", product=product)


@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_product():
    form = "CreatePostForm()"
    if form.validate_on_submit():
        new_post = Product()  # to do
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_products"))
    return render_template("make-product.html", form=form)


@app.route("/delete/<int:product_id>")
@admin_only
def delete_product(product_id):
    product_to_delete = "BlogPost.query.get(post_id)"
    db.session.delete(product_to_delete)
    db.session.commit()
    return redirect(url_for('get_products'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)