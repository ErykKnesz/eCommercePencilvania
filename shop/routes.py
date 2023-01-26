import functools
from functools import wraps

from flask import (render_template, redirect, url_for, flash, request,
                   abort, session)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_uploads import configure_uploads
from flask_login import login_user, LoginManager, current_user, logout_user
from sqlalchemy.exc import IntegrityError

from shop import app, db
from shop.models import User, Product, Address, Order, OrderItem
from shop.forms import (UserForm, LoginForm, CartForm, ProductForm,
                        images, AddressForm)
from cart_serializer import update_cart_quantity, get_cart_dict
from image_handler import save_img


configure_uploads(app, images)
login_manager = LoginManager()
login_manager.init_app(app)


def login_required(view_func):
    @functools.wraps(view_func)
    def check_permissions(*args, **kwargs):
        if current_user.is_authenticated:
            return view_func(*args, **kwargs)
        return redirect(url_for('login', next=request.path))
    return check_permissions


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


@app.route("/register", methods=["GET", "POST"])
def register():
    form = UserForm()
    if request.method == "POST" and form.validate_on_submit():
        pass_hash = generate_password_hash(form.data["password"],
                                           method="pbkdf2:sha256",
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
            flash("This email address is already used", "danger")
            return redirect(url_for("login"))
        return redirect(url_for("get_products"))
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    next_url = request.args.get("next")
    if request.method == "POST":
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.data["email"]).first()
            if user:
                if check_password_hash(user.password, form.data["password"]):
                    login_user(user)
                    session["logged_in"] = True
                    session.permanent = True  # Use cookie to store session.
                    flash("You are now logged in.", "success")
                    return redirect(next_url or url_for("get_products"))
                flash("Wrong password.", "danger")
                return redirect(url_for("login"))
            flash("Email address not found.", "danger")
            return redirect(url_for("login"))
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("get_products"))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/")
def get_products():
    products = Product.query.all()
    form = CartForm()
    return render_template("shop.html", products=products, form=form)


@app.route("/cart/add/", methods=["POST"])
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
            "name": "%s",
            "price": %f,
            "quantity": %d 
        }''' % (product.id, product.name, product.price, qty)
        session["cart"] += cart_contents + ";"  # string to save in session's cart
        session["cart"] = update_cart_quantity(session.get("cart"), increment=True)[1]
        flash("New item was added to your cart!", "success")
    return redirect(url_for("get_products"))


@app.route("/cart/update/", methods=["POST"])
def update_cart():
    form = CartForm()
    if form.validate_on_submit():
        if session.get("cart") is None:
            session["cart"] = ""
        ids = request.form.getlist("product_id")
        quantities = request.form.getlist("quantity")
        for product_id, qty in zip(ids, quantities):
            product = db.session.query(Product).get(product_id)
            cart_contents = '''{
                "product_id": %d,
                "name": "%s",
                "price": %f,
                "quantity": %d 
            }''' % (product.id, product.name, product.price, int(qty))
            session["cart"] += cart_contents + ";"
        session["cart"] = update_cart_quantity(session.get("cart"))[1]
        flash("Updated the cart successfully!", "success")
    return redirect(url_for("get_cart"))


@app.route("/cart/remove/<int:product_id>")
def remove_from_cart(product_id):
    product = db.session.query(Product).get(product_id)
    session["cart"] = update_cart_quantity(session.get("cart", ""),
                                           remove_id=product_id)[1]
    flash(f"Removed {product.name} from cart", "success")
    return redirect(url_for("get_cart"))


@app.route("/cart")
def get_cart():
    form = CartForm()
    cart = session.get("cart")
    total = 0
    if cart is not None:
        cart = get_cart_dict(cart)
        for product in cart:
            line_total = cart[product]["quantity"] * cart[product]["price"]
            cart[product]["line_total"] = line_total
            total += line_total
    else:
        cart = {}
    return render_template("cart.html", form=form, cart=cart,
                           total=total)


@app.route("/product/<int:product_id>")
def get_product(product_id):
    product = Product.query.get(product_id)
    form = CartForm()
    return render_template("product.html", product=product, form=form)


@app.route("/admin")
@admin_only
def admin_page():
    products = Product.query.all()
    return render_template("admin.html", products=products)


@app.route("/admin/product/add", methods=["GET", "POST"])
@admin_only
def add_product():
    form = ProductForm()
    if request.method == "POST":
        if form.validate_on_submit():
            filename = save_img(app.config["UPLOADED_PHOTOS_DEST"], form)
            product = Product(
                name=form.data["name"],
                description=form.data["description"],
                filename=filename,
                price=form.data["price"]
            )
            db.session.add(product)
            db.session.commit()
            return redirect(url_for("admin_page"))
    return render_template("new-product.html", form=form)


@app.route("/admin/product/edit/<int:product_id>", methods=["GET", "POST"])
@admin_only
def edit_product(product_id):
    product = Product.query.get(product_id)
    form = ProductForm(obj=product)
    if request.method == "POST":
        if form.validate_on_submit():
            filename = save_img(app.config["UPLOADED_PHOTOS_DEST"], form)
            product.name = form.data["name"]
            product.description = form.data["description"]
            product.filename = filename
            product.price = form.data["price"]
            db.session.add(product)
            db.session.commit()
            flash("Successfully edited product information", "success")
            return redirect(url_for("admin_page"))
    return render_template("edit-product.html", form=form, product_id=product_id)


@app.route("/admin/product/delete/<int:product_id>")
@admin_only
def delete_product(product_id):
    product = Product.query.get(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for("admin_page"))


@app.route("/checkout")
def checkout():
    cart = session.get("cart")
    total = 0
    if cart is not None:
        cart = get_cart_dict(cart)
        for product in cart:
            line_total = cart[product]["quantity"] * cart[product]["price"]
            cart[product]["line_total"] = line_total
            total += line_total
    else:
        cart = {}
    return render_template("checkout.html", cart=cart, total=total)


@app.route("/my-account")
@login_required
def my_account():
    user = User.query.get(current_user.id)
    form = AddressForm()
    addresses = Address.query.get(current_user.id)
    orders = Order.query.get(current_user.id)
    return render_template("my-account.html", user=user, form=form,
                           addresses=addresses, orders=orders)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
