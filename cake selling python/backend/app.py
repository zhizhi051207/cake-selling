from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from datetime import datetime
import json
import os
from models import Database

app = Flask(__name__,
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
app.secret_key = 'your-secret-key-here-change-in-production'
CORS(app)

# Initialize database
db = Database()

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/admin')
def admin():
    """管理员页面"""
    return render_template('admin.html')

@app.route('/api/cakes', methods=['GET'])
def get_cakes():
    """获取所有蛋糕"""
    cakes = db.get_all_cakes()
    return jsonify(cakes)

@app.route('/api/cakes/<int:cake_id>', methods=['GET'])
def get_cake(cake_id):
    """获取单个蛋糕详情"""
    cake = db.get_cake(cake_id)
    if cake:
        return jsonify(cake)
    return jsonify({'error': 'Cake not found'}), 404

@app.route('/api/cakes', methods=['POST'])
def add_cake():
    """添加新蛋糕"""
    data = request.json
    required_fields = ['name', 'description', 'price', 'category']

    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    cake_id = db.add_cake(
        name=data['name'],
        description=data['description'],
        price=float(data['price']),
        category=data['category'],
        image_url=data.get('image_url', ''),
        stock=int(data.get('stock', 0))
    )

    return jsonify({'id': cake_id, 'message': 'Cake added successfully'}), 201

@app.route('/api/cakes/<int:cake_id>', methods=['PUT'])
def update_cake(cake_id):
    """更新蛋糕信息"""
    data = request.json
    success = db.update_cake(
        cake_id=cake_id,
        name=data.get('name'),
        description=data.get('description'),
        price=data.get('price'),
        category=data.get('category'),
        image_url=data.get('image_url'),
        stock=data.get('stock')
    )

    if success:
        return jsonify({'message': 'Cake updated successfully'})
    return jsonify({'error': 'Cake not found'}), 404

@app.route('/api/cakes/<int:cake_id>', methods=['DELETE'])
def delete_cake(cake_id):
    """删除蛋糕"""
    success = db.delete_cake(cake_id)
    if success:
        return jsonify({'message': 'Cake deleted successfully'})
    return jsonify({'error': 'Cake not found'}), 404

@app.route('/api/cart', methods=['GET'])
def get_cart():
    """获取购物车"""
    if 'cart' not in session:
        session['cart'] = []
    return jsonify(session['cart'])

@app.route('/api/cart', methods=['POST'])
def add_to_cart():
    """添加到购物车"""
    data = request.json
    if 'cart' not in session:
        session['cart'] = []

    cake = db.get_cake(data['cake_id'])
    if not cake:
        return jsonify({'error': 'Cake not found'}), 404

    # 检查购物车中是否已有该商品
    cart_item = next((item for item in session['cart'] if item['cake_id'] == data['cake_id']), None)

    if cart_item:
        cart_item['quantity'] += data.get('quantity', 1)
    else:
        session['cart'].append({
            'cake_id': data['cake_id'],
            'name': cake['name'],
            'price': cake['price'],
            'quantity': data.get('quantity', 1),
            'image_url': cake['image_url']
        })

    session.modified = True
    return jsonify({'message': 'Added to cart', 'cart': session['cart']})

@app.route('/api/cart/<int:cake_id>', methods=['DELETE'])
def remove_from_cart(cake_id):
    """从购物车删除"""
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item['cake_id'] != cake_id]
        session.modified = True
    return jsonify({'message': 'Removed from cart'})

@app.route('/api/cart/clear', methods=['POST'])
def clear_cart():
    """清空购物车"""
    session['cart'] = []
    session.modified = True
    return jsonify({'message': 'Cart cleared'})

@app.route('/api/orders', methods=['POST'])
def create_order():
    """创建订单"""
    data = request.json

    if 'cart' not in session or not session['cart']:
        return jsonify({'error': 'Cart is empty'}), 400

    required_fields = ['customer_name', 'phone', 'address']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    # 计算总价
    total = sum(item['price'] * item['quantity'] for item in session['cart'])

    # 创建订单
    order_id = db.create_order(
        customer_name=data['customer_name'],
        phone=data['phone'],
        address=data['address'],
        total=total,
        items=session['cart']
    )

    # 清空购物车
    session['cart'] = []
    session.modified = True

    return jsonify({
        'order_id': order_id,
        'message': 'Order created successfully',
        'total': total
    }), 201

@app.route('/api/orders', methods=['GET'])
def get_orders():
    """获取所有订单"""
    orders = db.get_all_orders()
    return jsonify(orders)

@app.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """获取订单详情"""
    order = db.get_order(order_id)
    if order:
        return jsonify(order)
    return jsonify({'error': 'Order not found'}), 404

@app.route('/api/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """更新订单状态"""
    data = request.json
    success = db.update_order_status(order_id, data['status'])

    if success:
        return jsonify({'message': 'Order status updated'})
    return jsonify({'error': 'Order not found'}), 404

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取统计数据"""
    stats = db.get_statistics()
    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
