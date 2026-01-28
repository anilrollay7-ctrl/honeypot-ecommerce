"""
E-commerce API endpoints for the honeypot frontend
"""
from flask import Blueprint, jsonify, request
from functools import wraps
import jwt
from datetime import datetime, timedelta
from database import DatabaseHandler
import secrets
import hashlib

ecommerce = Blueprint('ecommerce', __name__, url_prefix='/api/ecommerce')
db = DatabaseHandler()

# Import advanced security
advanced_security = None  # Will be set after initialization

def set_advanced_security(sec):
    """Set the advanced security instance"""
    global advanced_security
    advanced_security = sec

# Secret key for JWT
SECRET_KEY = secrets.token_hex(32)

# MongoDB collections
USERS_COLLECTION = 'ecommerce_users'
ORDERS_COLLECTION = 'ecommerce_orders'
ACTIONS_COLLECTION = 'ecommerce_actions'

# Mock data for products
PRODUCTS = [
    {"id": 1, "name": "Gaming Laptop RTX 4090", "price": 2499, "category": "electronics", "description": "High-performance gaming laptop with RTX 4090", "image": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=400", "rating": 4.8, "reviews": 342, "discount": 15, "inStock": True},
    {"id": 2, "name": "Wireless Gaming Mouse", "price": 79, "category": "gaming", "description": "RGB wireless gaming mouse with 16000 DPI", "image": "https://images.unsplash.com/photo-1527814050087-3793815479db?w=400", "rating": 4.6, "reviews": 523, "discount": 0, "inStock": True},
    {"id": 3, "name": "Mechanical Keyboard RGB", "price": 129, "category": "gaming", "description": "Mechanical gaming keyboard with Cherry MX switches", "image": "https://images.unsplash.com/photo-1511467687858-23d96c32e4ae?w=400", "rating": 4.7, "reviews": 412, "discount": 10, "inStock": True},
    {"id": 4, "name": "4K Gaming Monitor 32\"", "price": 599, "category": "electronics", "description": "32-inch 4K monitor with 144Hz refresh rate", "image": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=400", "rating": 4.9, "reviews": 267, "discount": 20, "inStock": True},
    {"id": 5, "name": "Wireless Headphones", "price": 199, "category": "accessories", "description": "Premium noise-cancelling wireless headphones", "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400", "rating": 4.5, "reviews": 891, "discount": 0, "inStock": True},
    {"id": 6, "name": "Smart Watch Pro", "price": 399, "category": "accessories", "description": "Advanced smartwatch with health tracking", "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400", "rating": 4.4, "reviews": 612, "discount": 12, "inStock": True},
    {"id": 7, "name": "Gaming Chair Pro", "price": 349, "category": "gaming", "description": "Ergonomic gaming chair with lumbar support", "image": "https://images.unsplash.com/photo-1580480055273-228ff5388ef8?w=400", "rating": 4.6, "reviews": 298, "discount": 0, "inStock": True},
    {"id": 8, "name": "USB-C Hub 10-in-1", "price": 49, "category": "accessories", "description": "10-port USB-C hub with HDMI and ethernet", "image": "https://images.unsplash.com/photo-1625948515291-69613efd103f?w=400", "rating": 4.3, "reviews": 734, "discount": 5, "inStock": True},
    {"id": 9, "name": "Webcam 4K Pro", "price": 149, "category": "electronics", "description": "4K webcam with auto-focus and HDR", "image": "https://images.unsplash.com/photo-1587825140708-dfaf72ae4b04?w=400", "rating": 4.7, "reviews": 445, "discount": 0, "inStock": True},
    {"id": 10, "name": "Portable SSD 2TB", "price": 219, "category": "electronics", "description": "Ultra-fast portable SSD with 2TB storage", "image": "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=400", "rating": 4.8, "reviews": 523, "discount": 18, "inStock": True},
    {"id": 11, "name": "Graphics Tablet Pro", "price": 299, "category": "electronics", "description": "Professional graphics tablet for digital artists", "image": "https://images.unsplash.com/photo-1587825140708-dfaf72ae4b04?w=400", "rating": 4.6, "reviews": 178, "discount": 0, "inStock": True},
    {"id": 12, "name": "RGB LED Strip 5m", "price": 29, "category": "accessories", "description": "Smart RGB LED strip with app control", "image": "https://images.unsplash.com/photo-1626378803689-c6451f5c4926?w=400", "rating": 4.2, "reviews": 891, "discount": 0, "inStock": True},
]

def log_action(user_id, action_type, details):
    """Log all user actions to MongoDB"""
    action = {
        'user_id': user_id,
        'action_type': action_type,
        'details': details,
        'timestamp': datetime.utcnow().isoformat(),
        'ip_address': request.remote_addr,
        'user_agent': request.headers.get('User-Agent')
    }
    db.insert_document(ACTIONS_COLLECTION, action)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            token = token.replace('Bearer ', '')
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user = data['email']  # Changed from user_id to email
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

# Auth routes
@ecommerce.route('/auth/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    
    # Check if user exists in MongoDB
    existing_user = db.find_document(USERS_COLLECTION, {'email': email})
    if existing_user:
        log_action(None, 'register_failed', {'email': email, 'reason': 'user_exists'})
        return jsonify({'message': 'User already exists'}), 400
    
    # Create new user
    user_doc = {
        'name': data.get('name'),
        'email': email,
        'phone': data.get('phone', ''),
        'password': hashlib.sha256(data.get('password', '').encode()).hexdigest(),
        'address': {
            'street': '',
            'city': '',
            'state': '',
            'zip': '',
            'country': ''
        },
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }
    
    # Insert into MongoDB
    result = db.insert_document(USERS_COLLECTION, user_doc)
    user_id = str(result) if result else email
    
    # Log action
    log_action(user_id, 'register', {'email': email, 'name': data.get('name')})
    
    # Generate JWT token
    token = jwt.encode({
        'user_id': user_id,
        'email': email,
        'exp': datetime.utcnow() + timedelta(days=30)
    }, SECRET_KEY, algorithm='HS256')
    
    user_data = user_doc.copy()
    del user_data['password']
    user_data['id'] = user_id
    
    return jsonify({
        'token': token,
        'user': user_data
    }), 201

@ecommerce.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    ip = request.remote_addr
    
    # Check if user is blocked
    if advanced_security and advanced_security.is_user_blocked(email):
        log_action(None, 'login_blocked', {'email': email, 'reason': 'user_blocked'})
        return jsonify({'message': 'Account blocked due to suspicious activity'}), 403
    
    # Check if IP is blocked
    if advanced_security and advanced_security.is_ip_blocked(ip):
        log_action(None, 'login_blocked', {'email': email, 'reason': 'ip_blocked'})
        return jsonify({'message': 'Access denied'}), 403
    
    # Find user in MongoDB
    user = db.find_document(USERS_COLLECTION, {'email': email})
    
    if not user:
        log_action(None, 'login_failed', {'email': email, 'reason': 'user_not_found'})
        if advanced_security:
            advanced_security.log_failed_login(email, ip)
        return jsonify({'message': 'Invalid credentials'}), 401
    
    # Check password
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if user.get('password') != password_hash:
        log_action(None, 'login_failed', {'email': email, 'reason': 'wrong_password'})
        if advanced_security:
            advanced_security.log_failed_login(email, ip)
        return jsonify({'message': 'Invalid credentials'}), 401
    
    user_id = str(user.get('_id', email))
    
    # Log successful login
    log_action(user_id, 'login', {'email': email})
    if advanced_security:
        advanced_security.log_successful_login(email, ip)
        advanced_security.log_user_activity(email, 'login', {'success': True})
    
    # Generate JWT token
    token = jwt.encode({
        'user_id': user_id,
        'email': email,
        'exp': datetime.utcnow() + timedelta(days=30)
    }, SECRET_KEY, algorithm='HS256')
    
    user_data = {
        'id': user_id,
        'name': user.get('name'),
        'email': user.get('email'),
        'phone': user.get('phone', ''),
        'address': user.get('address', {}),
        'created_at': user.get('created_at')
    }
    
    return jsonify({
        'token': token,
        'user': user_data
    }), 200

@ecommerce.route('/auth/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    # Find user in MongoDB by email from token
    user = db.find_document(USERS_COLLECTION, {'email': current_user})
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    user_data = {
        'id': str(user.get('_id')),
        'name': user.get('name'),
        'email': user.get('email'),
        'phone': user.get('phone', ''),
        'address': user.get('address', {}),
        'created_at': user.get('created_at')
    }
    
    log_action(current_user, 'view_profile', {})
    
    return jsonify(user_data), 200

@ecommerce.route('/auth/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    try:
        data = request.json
        
        # Update user in MongoDB
        update_data = {
            'name': data.get('name'),
            'phone': data.get('phone', ''),
            'address': data.get('address', {}),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        result = db.update_document(USERS_COLLECTION, {'email': current_user}, update_data)
        
        if not result:
            return jsonify({'message': 'Failed to update profile'}), 500
        
        log_action(current_user, 'update_profile', update_data)
        
        # Get updated user
        user = db.find_document(USERS_COLLECTION, {'email': current_user})
        
        if not user:
            return jsonify({'message': 'User not found after update'}), 404
        
        user_data = {
            'id': str(user.get('_id')),
            'name': user.get('name'),
            'email': user.get('email'),
            'phone': user.get('phone', ''),
            'address': user.get('address', {}),
            'created_at': user.get('created_at')
        }
        
        return jsonify(user_data), 200
    except Exception as e:
        print(f"Error in update_profile: {str(e)}")
        return jsonify({'message': f'Error updating profile: {str(e)}'}), 500

# Products routes
@ecommerce.route('/products', methods=['GET'])
def get_products():
    category = request.args.get('category')
    search = request.args.get('search', '').lower()
    sort = request.args.get('sort', 'popular')
    limit = request.args.get('limit', type=int)
    featured = request.args.get('featured', 'false').lower() == 'true'
    
    log_action(None, 'browse_products', {'category': category, 'search': search, 'sort': sort})
    
    # Log activity if user is authenticated
    token = request.headers.get('Authorization')
    if token and advanced_security:
        try:
            token = token.replace('Bearer ', '')
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            email = data.get('email')
            advanced_security.log_user_activity(email, 'browse_products', {'category': category, 'search': search})
        except:
            pass
    
    filtered_products = PRODUCTS.copy()
    
    # Filter by category
    if category and category != 'all':
        filtered_products = [p for p in filtered_products if p['category'].lower() == category.lower()]
    
    # Filter by search
    if search:
        filtered_products = [p for p in filtered_products 
                            if search in p['name'].lower() or search in p['description'].lower()]
    
    # Sort products
    if sort == 'price-low':
        filtered_products.sort(key=lambda x: x['price'])
    elif sort == 'price-high':
        filtered_products.sort(key=lambda x: x['price'], reverse=True)
    elif sort == 'rating':
        filtered_products.sort(key=lambda x: x.get('rating', 0), reverse=True)
    elif sort == 'newest':
        filtered_products.reverse()
    
    # Limit results
    if limit:
        filtered_products = filtered_products[:limit]
    
    # Featured products
    if featured:
        filtered_products = [p for p in filtered_products if p.get('discount', 0) > 0][:8]
    
    return jsonify({'products': filtered_products}), 200

@ecommerce.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = next((p for p in PRODUCTS if p['id'] == product_id), None)
    if not product:
        return jsonify({'message': 'Product not found'}), 404
    
    log_action(None, 'view_product', {'product_id': product_id})
    
    # Log activity if user is authenticated
    token = request.headers.get('Authorization')
    if token and advanced_security:
        try:
            token = token.replace('Bearer ', '')
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            email = data.get('email')
            advanced_security.log_user_activity(email, 'view_product', {'product_id': product_id, 'product_name': product['name']})
        except:
            pass
    
    log_action(None, 'view_product', {'product_id': product_id, 'product_name': product['name']})
    
    return jsonify(product), 200

@ecommerce.route('/categories', methods=['GET'])
def get_categories():
    categories = list(set([p['category'] for p in PRODUCTS]))
    return jsonify(categories), 200

# Orders routes with MongoDB and payment
@ecommerce.route('/orders', methods=['POST'])
@token_required
def create_order(current_user):
    try:
        data = request.json
        
        # Validate order data
        items = data.get('items', [])
        if not items:
            return jsonify({'message': 'No items in order'}), 400
        
        # Validate shipping address
        shipping_address = data.get('shippingAddress') or data.get('shipping_address', {})
        if not shipping_address or not shipping_address.get('street'):
            return jsonify({'message': 'Shipping address is required'}), 400
        
        # Calculate total
        total = sum(item['price'] * item['quantity'] for item in items)
        
        # Process payment (dummy)
        payment_data = data.get('paymentDetails') or data.get('payment', {})
        payment_method = payment_data.get('method', 'credit_card')
        
        # Create order in MongoDB
        order_doc = {
            'order_id': secrets.token_hex(8),
            'user_email': current_user,
            'items': items,
            'total': total,
            'payment': {
                'method': payment_method,
                'status': 'paid',
                'transaction_id': f'TXN-{secrets.token_hex(6).upper()}',
                'paid_at': datetime.utcnow().isoformat()
            },
            'shipping_address': shipping_address,
            'status': 'confirmed',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        result = db.insert_document(ORDERS_COLLECTION, order_doc)
        
        if not result:
            return jsonify({'message': 'Failed to create order'}), 500
        
        # Log checkout action with advanced security
        if advanced_security:
            advanced_security.log_user_activity(current_user, 'checkout', {
                'order_id': order_doc['order_id'],
                'total': total,
                'items_count': len(items),
                'payment_method': payment_method
            })
        
        # Log order creation
        log_action(current_user, 'create_order', {
            'order_id': order_doc['order_id'],
            'total': total,
            'items_count': len(items),
            'payment_method': payment_method
        })
        
        return jsonify({
            'order_id': order_doc['order_id'],
            'status': 'confirmed',
            'transaction_id': order_doc['payment']['transaction_id'],
            'message': 'Order placed successfully'
        }), 201
    except Exception as e:
        print(f"Error in create_order: {str(e)}")
        return jsonify({'message': f'Error creating order: {str(e)}'}), 500

@ecommerce.route('/orders', methods=['GET'])
@token_required
def get_orders(current_user):
    # Find all orders for the current user
    orders = db.find_documents(ORDERS_COLLECTION, {'user_email': current_user})
    
    # Format orders for response
    orders_list = []
    for order in orders:
        orders_list.append({
            'id': str(order.get('_id')),
            'order_id': order.get('order_id'),
            'items': order.get('items', []),
            'total': order.get('total'),
            'status': order.get('status'),
            'payment': order.get('payment', {}),
            'shipping_address': order.get('shipping_address', {}),
            'created_at': order.get('created_at'),
            'updated_at': order.get('updated_at')
        })
    
    # Sort by created_at descending
    orders_list.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    log_action(current_user, 'view_orders', {'count': len(orders_list)})
    
    return jsonify(orders_list), 200

@ecommerce.route('/orders/<order_id>', methods=['GET'])
@token_required
def get_order(current_user, order_id):
    # Find specific order
    order = db.find_document(ORDERS_COLLECTION, {
        'order_id': order_id,
        'user_email': current_user
    })
    
    if not order:
        return jsonify({'message': 'Order not found'}), 404
    
    order_data = {
        'id': str(order.get('_id')),
        'order_id': order.get('order_id'),
        'items': order.get('items', []),
        'total': order.get('total'),
        'status': order.get('status'),
        'payment': order.get('payment', {}),
        'shipping_address': order.get('shipping_address', {}),
        'created_at': order.get('created_at'),
        'updated_at': order.get('updated_at')
    }
    
    log_action(current_user, 'view_order_details', {'order_id': order_id})
    
    return jsonify(order_data), 200
