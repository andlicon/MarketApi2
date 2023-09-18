"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User, Product, ProductOrder, Order, OrderStatus
from api.utils import generate_sitemap, APIException
from sqlalchemy.sql import func

api = Blueprint('api', __name__)


# get All users
@api.route('/users', methods=['GET'])
def get_all_user():

    user_list = User.query.all()
    serialized = list(map(lambda user: user.serialize(), user_list))

    return jsonify(serialized), 200

# add a new user
@api.route('/users', methods=['POST'])
def add_user():
    if not request.is_json:
        return jsonify({'msg': 'Body must be a JSON object'}), 400

    body = request.get_json()
    name = body.get('name')
    email = body.get('email')
    if None in [name, email]:
        return jsonify({'msg': 'Wrong properties'}), 400

    any_user = User.query.filter_by(email=email).one_or_none()
    if any_user is not None:
        return jsonify({'msg': 'Email already chosen'}), 400

    user = User(name=name, email=email)

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({'msg': 'Some internal error'}), 500

    return jsonify({'msg': 'User added'}), 202


# get All products
@api.route('/products', methods=['GET'])
def get_all_products():

    product_list = Product.query.all()
    serialized = list(map(lambda product: product.serialize(), product_list))

    return jsonify(serialized), 200

# add a new product
@api.route('/products', methods=['POST'])
def add_product():
    if not request.is_json:
        return jsonify({'msg': 'Body must be a JSON object'}), 400

    body = request.get_json()
    name = body.get('name')
    price = body.get('price')
    if None in [name, price]:
        return jsonify({'msg': 'Wrong properties'}), 400

    any_product = Product.query.filter_by(name=name).one_or_none()
    if any_product is not None:
        return jsonify({'msg': 'There is a product already.'}), 400

    product = Product(name=name, price=price)

    try:
        db.session.add(product)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({'msg': 'Some internal error'}), 500

    return jsonify({'msg': 'Product added'}), 202


# add a new product
@api.route('/products/<int:id>', methods=['DELETE'])
def remove_product(id):
    product = Product.query.filter_by(id=id).one_or_none()
    if product is None:
        return jsonify({'msg': 'Product not found'}), 404

    try:
        db.session.delete(product)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({'msg': 'Some internal error'}), 500

    return jsonify({'msg': 'Product deleted'}), 200


# put a new product
@api.route('/products/<int:id>', methods=['PUT'])
def put_product(id):
    if not request.is_json:
        return jsonify({'msg': 'Body must be a JSON object'}), 400

    product = Product.query.filter_by(id=id).one_or_none()
    if product is None:
        return jsonify({'msg': 'Product not found'}), 404

    body = request.get_json()
    name = body.get('name')
    price = body.get('price')
    if None in [name, price]:
        return jsonify({'msg': 'Wrong properties'}), 400

    product.name = name
    product.price = price

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({'msg': 'Some internal error'}), 500

    return jsonify({'msg': 'Product updated'}), 200


# patch a new product
@api.route('/products/<int:id>', methods=['PATCH'])
def patch_product(id):
    if not request.is_json:
        return jsonify({'msg': 'Body must be a JSON object'}), 400

    product = Product.query.filter_by(id=id).one_or_none()
    if product is None:
        return jsonify({'msg': 'Product not found'}), 404

    body = request.get_json()
    name = body.get('name')
    price = body.get('price')

    product.name = name if name is not None else product.name
    product.price = price if price is not None else product.price

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({'msg': 'Some internal error'}), 500

    return jsonify({'msg': 'Product updated'}), 200


# all product user sale
@api.route('/sales/product/user/<int:id>', methods=['GET'])
def user_product_sale(id):
    user = User.query.filter_by(id=id).one_or_none()
    if user is None:
        return jsonify({'msg': 'User not found'}), 404

    order_list = Order.query.filter_by(user_id=user.id, status=OrderStatus.SALE).all()

    product_list = []
    for order in order_list:
        product_order_list = ProductOrder.query.filter_by(order_id=order.id).all()
        for product_order in product_order_list:
            product = product_order.product.serialize()
            if product in product_list:
                continue
            product_list.append(product)

    return jsonify(product_list), 200


# all product by order
@api.route('/order/<int:id>', methods=['GET'])
def get_order(id):
    order = Order.query.filter_by(id=id).one_or_none()
    if order is None:
        return jsonify({'msg': 'Order not found'}), 404

    product_order_list = ProductOrder.query.filter_by(order_id=id).all()
    serialized = []
    for product_order in product_order_list:
        obj = {
            "amount": product_order.amount,
            "product": product_order.product.serialize()
        }
        serialized.append(obj)


    return jsonify(serialized), 200


# all user that has bought
@api.route('/user/has-bought', methods=['GET'])
def user_has_bought():
    order_list = Order.query.filter_by(status=OrderStatus.SALE).distinct(Order.user_id).all()

    user_list = list(map(lambda order: order.user.serialize(), order_list))

    return jsonify(user_list), 200