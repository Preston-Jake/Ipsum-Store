from flask import Flask, request, abort, g
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful import Api, Resource
from passlib.apps import custom_app_context as pwd_context
from flask_httpauth import HTTPBasicAuth
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ipsum.db'
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)
auth = HTTPBasicAuth()


# =============================== AUTH ===============================


@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    User = User.verify_auth_token(username_or_token)
    if not User:
        # try to authenticate with username/password
        User = User.query.filter_by(username=username_or_token).first()
        if not User or not User.verify_password(password):
            return False
    g.User = User
    return True


#  =============================== User ===============================


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(50))
    username = db.Column(db.String(255))
    password_hash = db.Column(db.String(32), index=True)
    billing_address = db.relationship(
        "Address", foreign_keys=['billing_address_id']
    )
    billing_address_id = db.Column(
        db.Integer, db.ForeignKey("address.id"), nullable=True
    )
    shipping_address = db.relationship(
        "Address", foreign_keys=['shipping_address_id']
    )
    shipping_address_id = db.Column(
        db.Integer, db.ForeignKey("address.id"), nullable=True
    )

    def __repr__(self):
        return '<User %s>' % self.first_name

    def hash_pasword(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        User = User.query.get(data['id'])
        return User


class UserSchema(ma.Schema):
    class Meta:
        fields = (
            "billing_address_id",
            "email"
            "first_name",
            "id",
            "last_name",
            "shipping_address_id",
            )


User_schema = UserSchema()
Users_schema = UserSchema(many=True)


class UserListResource(Resource):
    def get(self):
        Users = User.query.all()
        return Users_schema.dump(Users)

    def post(self):
        email = request.json['email']
        password = request.json['password']
        if email is None or password is None:
            api.abort(400)
        if User.query.filter_by(email=email).first() is not None:
            api.abort(400)
        User = User(
            billing_address_id=request.json['billing_address_id'],
            email=email,
            first_name=request.json['first_name'],
            is_admin=request.json['is_admin'],
            last_name=request.json['last_name'],
            shipping_address_id=request.json['shipping_address_id']
        )
        User.hash_pasword(password)
        db.session.add(User)
        db.session.commit()
        return User_schema.dump(User)


class UserResource(Resource):
    @auth.login_required
    def get(self, User_id):
        User = User.query.get_or_404(User_id)
        return User_schema.dump(User)

    def patch(self, User_id):
        User = User.query.get_or_404(User_id)

        if 'first_name' in request.json:
            User.first_name = request.json['first_name']
        if 'last_name' in request.json:
            User.last_name = request.json['last_name']
        if 'is_admin' in request.json:
            User.is_admin = request.json['is_admin']
        if 'billing_address_id' in request.json:
            User.billing_address_id = request.json['billing_address_id']
        if 'shipping_address_id' in request.json:
            User.shipping_address_id = request.json['shipping_address_id']

        db.session.commit()
        return User_schema.dump(User)

    def delete(self, User_id):
        User = User.query.get_or_404(User_id)
        db.session.delete(User)
        db.session.commit()
        return '', 204


api.add_resource(UserListResource, '/Users')
api.add_resource(UserResource, '/Users/<int:User_id>')


# =============================== ADDRESS ===============================


class Address(db.Model):
    address_1 = db.Column(db.String(255))
    address_2 = db.Column(db.String(255))
    city = db.Column(db.String(255))
    country = db.Column(db.String(255))
    id = db.Column(db.Integer, primary_key=True)
    postal_code = db.Column(db.String(255))
    state = db.Column(db.String(255))

    def __repr__(self):
        return '<Address %s>' % self.address_1


class AddressSchema(ma.Schema):
    class Meta:
        fields = (
            "address_1",
            "address_2",
            "city",
            "country",
            "id",
            "postal_code",
            "state"
            )


address_schema = AddressSchema()
addresses_schema = AddressSchema(many=True)


class AddressListResource(Resource):
    def get(self):
        addresses = Address.query.all()
        return addresses_schema.dump(addresses)

    def post(self):
        new_address = Address(
            address_1=request.json['address_1'],
            address_2=request.json['address_2'],
            city=request.json['city'],
            country=request.json['country'],
            postal_code=request.json['postal_code'],
            state=request.json['state']
        )
        db.session.add(new_address)
        db.session.commit()
        return address_schema.dump(new_address)


class AddressResource(Resource):
    def get(self, address_id):
        address = Address.query.get_or_404(address_id)
        return address_schema.dump(address)

    def patch(self, address_id):
        address = Address.query.get_or_404(address_id)

        if 'address_1' in request.json:
            address.address_1 = request.json['address_1']
        if 'address_2' in request.json:
            address.address_2 = request.json['address_2']
        if 'city' in request.json:
            address.city = request.json['city']
        if 'state' in request.json:
            address.state = request.json['state']
        if 'country' in request.json:
            address.country = request.json['country']
        if 'postal_code' in request.json:
            address.postal_code = request.json['postal_code']
        db.session.commit()
        return address_schema.dump(address)

    def delete(self, address_id):
        address = Address.query.get_or_404(address_id)
        db.session.delete(address)
        db.session.commit()


api.add_resource(AddressListResource, '/addresses')
api.add_resource(AddressResource, '/addresses/<int:address_id>')


# =============================== PRODUCT ===============================


class Product(db.Model):
    description = db.Column(db.String())
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    options = db.relationship("Option")

    def __repr__(self):
        return '<Product %s>' % self.name


class ProductSchema(ma.Schema):
    class Meta:
        fields = (
            "description",
            "id",
            "name",
            )


product_schema = ProductSchema()
products_schema = ProductSchema(many=True)


class ProductListResource(Resource):
    def get(self):
        products = Product.query.all()
        return products_schema.dump(products)

    def post(self):
        new_product = Product(
            description=request.json['description'],
            name=request.json['name'],
        )
        db.session.add(new_product)
        db.session.commit()
        return product_schema.dump(new_product)


class ProductResource(Resource):
    def get(self, product_id):
        product = Product.query.get_or_404(product_id)
        return product_schema.dump(product)

    def patch(self, product_id):
        product = Product.query.get_or_404(product_id)

        if 'name' in request.json:
            product.name = request.json['name']
        if 'description' in request.json:
            product.description = request.json['description']

        db.session.commit()
        return product_schema.dump(product)

    def delete(self, product_id):
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        return '', 204


api.add_resource(ProductListResource, '/products')
api.add_resource(ProductResource, '/products/<int:product_id>')


# =============================== OPTION ===============================


class Option(db.Model):
    color = db.Column(db.String())
    id = db.Column(db.Integer, primary_key=True)
    image_source = db.Column(db.String())
    percent_off = db.Column(db.Integer())
    product = db.relationship(
        "Product",
        foreign_keys="Option.product_id"
        )
    product_id = db.Column(
        db.Integer,
        db.ForeignKey("product.id")
        )
    retail_price = db.Column(db.Integer())
    wholesale_price = db.Column(db.Integer())

    def __repr__(self):
        return '<Option %s>' % self.color


class OptionSchema(ma.Schema):
    class Meta:
        fields = (
            "color",
            "id",
            "image_source",
            "percent_off",
            "product_id",
            "retail_price",
            "wholesale_price"
            )


option_schema = OptionSchema()
options_schema = OptionSchema(many=True)


class OptionListResource(Resource):
    def get(self):
        options = Option.query.all()
        return options_schema.dump(options)

    def post(self):
        new_option = Option(
            color=request.json['color'],
            image_source=request.json['image_source'],
            percent_off=request.json['percent_off'],
            product_id=request.json['product_id'],
            retail_price=request.json['retail_price'],
            wholesale_price=request.json['wholesale_price']
        )
        db.session.add(new_option)
        db.session.commit()
        option_schema.dump(new_option)


class OptionResource(Resource):
    def get(self, option_id):
        option = Option.query.get_or_404(option_id)
        return option_schema.dump(option)

    def patch(self, option_id):
        option = Option.quert.get_or_404(option_id)

        if 'color' in request.json:
            option.color = request.json['color']
        if 'image_source' in request.json:
            option.image_source = request.json['image_source']
        if 'percent_off' in request.json:
            option.percent_off = request.json['percent_off']
        if 'product_id' in request.json:
            option.product_id = request.json['product_id']
        if 'retail_price' in request.json:
            option.retail_price = request.json['retail_price']
        if 'wholesale_price' in request.json:
            option.wholesale_price = request.json['wholesale_price']

        db.session.commit()
        return option_schema.dump(option)

    def delete(self, option_id):
        option = Option.query.get_or_404(option_id)
        db.session.delete(option)
        db.session.commit()
        return '', 204


api.add_resource(OptionListResource, '/options')
api.add_resource(OptionResource, '/options/<int:option_id>')


# =============================== CATEGORY ===============================


# class Category (db.Model):
#     gender = db.Column(db.String())
#     id = db.Column(db.Integer, primary_key=True)
#     product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
#     type = db.Column(db.String())

#     def __repr__(self):
#         return '<Option %s>' % self.product_id


# class CategorySchema(ma.Schema):
#     class Meta:
#         fields = (
#             "gender",
#             "id",
#             "product_id",
#             "type"
#         )


# category_schema = CategorySchema()
# categories_schema = CategorySchema(many=True)


# class CategoryListResource(Resource):
#     def get(self):
#         categories = Category.query.all()
#         return categories_schema(categories)

#     def post(self):
#         new_category = Category(
#             gender=request.json['gender'],
#             product_id=request.json['product_id'],
#             type=request.json['type']
#         )
#         db.session.add(new_category)
#         db.session.commit()
#         return category_schema(new_category)


# class CategoryResource(Resource):
#     def get(self, category_id):
#         category = Category.query.get_or_404(category_id)
#         return category_schema.dump(category)

#     def patch(self, category_id):
#         category = Category.query.get_or_404(category_id)

#         if 'gender' in request.json:
#             category.gender = request.json['gender']
#         if 'product_id' in request.json:
#             category.product_id = request.json['product_id']
#         if 'type' in request.json:
#             category.type = request.json['type']

#         db.session.commit()
#         return category_schema(category)

#     def delete(self, category_id):
#         category = Category.query.get_or_404(category_id)
#         db.session.delete(category)
#         db.session.commit()
#         return '', 204


# api.add_resource(CategoryListResource, '/categories')
# api.add_resource(CategoryResource, '/products/<int:category_id>')


# =============================== CART ===============================


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    User_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    option_id = db.Column(db.Integer, db.ForeignKey('option.id'))
    User = db.relationship("User")
    option = db.relationship("Option")


class CartSchema(ma.Schema):
    class Meta:
        fields = (
            "id",
            "User_id",
            "option_id"
        )


cart_schema = CartSchema()
carts_schema = CartSchema(many=True)


class CartListResource(Resource):
    def get(self):
        carts = Cart.query.all()
        return carts_schema.dump(carts)

    def post(self):
        new_cart = Cart(
            User_id=request.json['User_id'],
            option_id=request.json['option_id']
        )
        db.session.add(new_cart)
        db.session.commit()
        cart_schema.dump(new_cart)


class CartResource(Resource):
    def get(self, cart_id):
        cart = Cart.query.get_or_404(cart_id)
        return cart_schema.dump(cart)

    def patch(self, cart_id):
        cart = Cart.query.get_or_404(cart_id)

        if 'User_id' in request.json:
            cart.User_id = request.json['User_id']
        if 'option_id' in request.json:
            cart.option_id = request.json['option_id']

        db.session.commit()
        return cart_schema.dump(cart)


api.add_resource(CartListResource, '/carts')
api.add_resource(CartResource, '/carts/<int:cart_id>')

if __name__ == '__main__':
    app.run(debug=True)
