from flask import Flask, request # change
from flask_sqlalchemy import SQLAlchemy, Table, Column, Integer, ForeignKey
from flask_marshmallow import Marshmallow # new
from flask_restful import Api, Resource # new

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ipsum.db'
db = SQLAlchemy(app)
ma = Marshmallow(app) # new
api = Api(app) # new

# Member Model
class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    member_address_id = db.Column(db.Integer, ForeignKey('address.id'))
    is_admin = db.Column(db.Boolean()) # look database boolean for sqlA

class MemberSchema(ma.Schema):
    class Meta:
        fields = ("id", "first_name", "last_name", "member_address_id", "is_admin")

member_schema = MemberSchema()
member_schema = MemberSchema(many=True)

#Member CRUD functions
class MemberListResource(Resource):
    def get(self):
        members = Product.query.all()
        return member_schema.dump(members)
    
    def post(self):
        new_member = Member(
            first_name=request.json['first_name'],
            last_name=request.json['last_name'],
            member_address_id=request.json['member_address_id'],
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
        if 'member_address_id' in request.json:
            member.member_address_id = request.json['member_address_id']
        if 'is_admin' in request.json:
            member.is_admin = request.json['is_admin']

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


#Member Address
# class MemberAddress(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     address_1 = db.Column(db.String(255))
#     address_2 = db.Column(db.String(255))
#     city = db.Column(db.String(255))
#     state = db.Column(db.String(255))
#     country = db.Column(db.String(255))
#     postal_code = db.Column(db.Integer)

# class MemberAddressSchema(ma.Schema):
#     class Meta:
#         fields = ("id", "address_1", "address_2", "city", "state", "country", "postal_code")

# Product Model & Schema
class Product(db.Model):
    __tabelname__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    description = db.Column(db.String())
    product_option_id = db.Column(db.Integer, ForeignKey('ProductOption.id'))
    product_category_id = db.Column(db.Integer, ForeignKey('ProductCategory.id'))
    
    def __repr__(self):
        return '<Product %s>' % self.name

class ProductSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "description", "product_option_id", "product_category_id")

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

#Product CRUD functions

class ProductListResource(Resource):
    def get(self):
        products = Product.query.all()
        return products_schema.dump(products)
    
    def post(self):
        new_product = Product(
            name=request.json['name'],
            description=request.json['description'],
            product_option_id=request.json['product_option_id'],
            product_category_id=request.json['product_category_id']
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
        if 'product_option_id' in request.json:
            product.product_option_id = request.json['product_option_id']
        if 'product_category_id' in request.json:
            product.product_category_id = request.json['product_category_id']

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