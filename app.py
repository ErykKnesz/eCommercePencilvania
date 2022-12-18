from shop import app
from shop.models import db, User, Product


@app.shell_context_processor
def make_shell_context():
    return {
       "db": db,
       "User": User,
       "Product": Product
    }


if __name__ == "__main__":
    app.run(debug=True)