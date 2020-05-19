from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful import Api, Resource


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ipsum.db'
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)


class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    is_admin = db.Column(db.Boolean, unique=False, default=False)

    def __repr__(self):
        return '<Member %s>' % self.first_name


class MemberSchema(ma.Schema):
    class Meta:
        fields = ("id", "first_name", "last_name", "is_admin")


member_schema = MemberSchema()
members_schema = MemberSchema(many=True)

# Member CRUD functions


class MemberListResource(Resource):
    def get(self):
        members = Member.query.all()
        return members_schema.dump(members)

    def post(self):
        new_member = Member(
            first_name=request.json['first_name'],
            last_name=request.json['last_name'],
            is_admin=request.json['is_admin']
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
        # if 'member_address_id' in request.json:
        #     member.member_address_id = request.json['member_address_id']

        db.session.commit()
        return member_schema.dump(member)

    def delete(self, member_id):
        member = Member.query.get_or_404(member_id)
        db.session.delete(member)
        db.session.commit()
        return '', 204

# Member routing


api.add_resource(MemberListResource, '/members')
api.add_resource(MemberResource, '/members/<int:member_id>')


class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address_1 = db.Column(db.String(255), nullable=True)
    address_2 = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(255), nullable=True)
    state = db.Column(db.String(255), nullable=True)
    country = db.Column(db.String(255), nullable=True)
    postal_code = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return '<Address %s>' % self.address_1


class AddressSchema(ma.Schema):
    class Meta:
        fields = (
            "id",
            "address_1",
            "address_2", "city",
            "state",
            "country",
            "postal_code"
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
            state=request.json['state'],
            country=request.json['country'],
            postal_code=request.json['postal_code']
        )
        db.session.add(new_address)
        db.session.commit()
        return address_schema.dump(new_address)


api.add_resource(AddressListResource, '/addresses')


# Product Model & Schema
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    description = db.Column(db.String())

    # product_option_id = db.Column(db.Integer, ForeignKey('ProductOption.id'))
    # product_category_id = db.Column(db.Integer, ForeignKey('ProductCategory.id'))

    def __repr__(self):
        return '<Product %s>' % self.name


class ProductSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "description")


product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

# Product CRUD functions


class ProductListResource(Resource):
    def get(self):
        products = Product.query.all()
        return products_schema.dump(products)

    def post(self):
        new_product = Product(
            name=request.json['name'],
            description=request.json['description'],

            # product_option_id=request.json['product_option_id'],
            # product_category_id=request.json['product_category_id']
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
        # if 'product_option_id' in request.json:
        #     product.product_option_id = request.json['product_option_id']
        # if 'product_category_id' in request.json:
        #     product.product_category_id = request.json['product_category_id']

        db.session.commit()
        return product_schema.dump(product)

    def delete(self, product_id):
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        return '', 204

# product routing


api.add_resource(ProductListResource, '/products')
api.add_resource(ProductResource, '/products/<int:product_id>')


# Product Option Model & Schema
# class ProductOption(db.Model):
#     __tabelname__ = 'product_option'
#     id = db.Column(db.Integer, primary_key=True)
#     product_id = db.Column(db.Integer, ForeignKey('product.id'))
#     color = db.Column(db.String(50))
#     wholesale_price = db.Column()
#     retail_price = db.Column()
#     precent_off = db.Column()
#     image_source = db.Column()

# Product Category Model & Schema

# class ProductCategory (db.Model):
#     __tabelname__ = 'product_category'
#     id = db.Column(db.Integer, primary_key=True)
#     product_type = db.Column(db.String)
#     product_gender = db.Column(db.String)


if __name__ == '__main__':
    app.run(debug=True)
