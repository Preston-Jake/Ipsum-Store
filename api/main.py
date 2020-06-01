from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful import Api, Resource


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ipsum.db'
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)

# =============================== MEMBER ===============================


class Member(db.Model):
    first_name = db.Column(db.String(50))
    id = db.Column(db.Integer, primary_key=True)
    is_admin = db.Column(db.Boolean, unique=False, default=False)
    last_name = db.Column(db.String(50))

    billing_address_id = db.Column(
        db.Integer,
        db.ForeignKey("address.id")
        )
    shipping_address_id = db.Column(
        db.Integer,
        db.ForeignKey("address.id")
    )

    billing_address = db.relationship(
        "Address",
        foreign_keys=[billing_address_id]
        )
    shipping_address = db.relationship(
        "Address",
        foreign_keys=[shipping_address_id]
        )

    def __repr__(self):
        return '<Member %s>' % self.first_name


class MemberSchema(ma.Schema):
    class Meta:
        fields = (
            "billing_address_id",
            "first_name",
            "id",
            "is_admin",
            "last_name",
            "shipping_address_id"
            )


member_schema = MemberSchema()
members_schema = MemberSchema(many=True)


class MemberListResource(Resource):
    def get(self):
        members = Member.query.all()
        return members_schema.dump(members)

    def post(self):
        new_member = Member(
            billing_address_id=request.json['billing_address_id'],
            first_name=request.json['first_name'],
            is_admin=request.json['is_admin'],
            last_name=request.json['last_name'],
            shipping_address_id=request.json['shipping_address_id']
        )
        db.session.add(new_member)
        db.session.commit()
        return member_schema.dump(new_member)


class MemberResource(Resource):
    def get(self, member_id):
        member = Member.query.get_or_404(member_id)
        return member_schema.dump(member)

    def patch(self, member_id):
        member = Member.query.get_or_404(member_id)

        if 'first_name' in request.json:
            member.first_name = request.json['first_name']
        if 'last_name' in request.json:
            member.last_name = request.json['last_name']
        if 'is_admin' in request.json:
            member.is_admin = request.json['is_admin']
        if 'billing_address_id' in request.json:
            member.billing_address_id = request.json['billing_address_id']
        if 'shipping_address_id' in request.json:
            member.shipping_address_id = request.json['shipping_address_id']

        db.session.commit()
        return member_schema.dump(member)

    def delete(self, member_id):
        member = Member.query.get_or_404(member_id)
        db.session.delete(member)
        db.session.commit()
        return '', 204


api.add_resource(MemberListResource, '/members')
api.add_resource(MemberResource, '/members/<int:member_id>')

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


class Category (db.Model):
    gender = db.Column(db.String())
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    type = db.Column(db.String())

    def __repr__(self):
        return '<Option %s>' % self.product_id


class CategorySchema(ma.Schema):
    class Meta:
        fields = (
            "gender",
            "id",
            "product_id",
            "type"
        )


category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)


class CategoryListResource(Resource):
    def get(self):
        categories = Category.query.all()
        return categories_schema(categories)

    def post(self):
        new_category = Category(
            gender=request.json['gender'],
            product_id=request.json['product_id'],
            type=request.json['type']
        )
        db.session.add(new_category)
        db.session.commit()
        return category_schema(new_category)


class CategoryResource(Resource):
    def get(self, category_id):
        category = Category.query.get_or_404(category_id)
        return category_schema.dump(category)

    def patch(self, category_id):
        category = Category.query.get_or_404(category_id)

        if 'gender' in request.json:
            category.gender = request.json['gender']
        if 'product_id' in request.json:
            category.product_id = request.json['product_id']
        if 'type' in request.json:
            category.type = request.json['type']

        db.session.commit()
        return category_schema(category)

    def delete(self, category_id):
        category = Category.query.get_or_404(category_id)
        db.session.delete(category)
        db.session.commit()
        return '', 204


api.add_resource(CategoryListResource, '/categories')
api.add_resource(CategoryResource, '/products/<int:category_id>')

# =============================== CART ===============================
# join table between meember and option


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    option_id = db.Column(db.Integer, db.ForeignKey('option.id'))
    member = db.relationship("Member")
    option = db.relationship("Option")


class CartSchema(ma.Schema):
    class Meta:
        fields = (
            "id",
            "member_id",
            "option_id"
        )


cart_schema = CartSchema()
carts_schema = CartSchema(many=True)


class CartListResource(Resource):
    def get(self):
        carts = Cart.quert.all()
        return carts_schema.dump(carts)

    def post(self):
        new_cart = Cart(
            member_id=request.json['member_id'],
            option_id=request.json['option_id']
        )
        db.session.add(new_cart)
        db.session.commit()
        cart_schema.dump(new_cart)



if __name__ == '__main__':
    app.run(debug=True)
