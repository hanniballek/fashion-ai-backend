from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
import random

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# قاعدة بيانات مبسطة للمستخدمين (في الإنتاج يجب استخدام قاعدة بيانات حقيقية)
users = {
    "user1@example.com": {
        "id": "1",
        "email": "user1@example.com",
        "password": "password123",
        "name": "مستخدم تجريبي",
        "preferences": ["عصري", "رسمي", "أنيق"]
    }
}

# قاعدة بيانات مبسطة للمنتجات
products = [
    {
        "id": "1",
        "name": "قميص أبيض كلاسيكي",
        "description": "قميص أبيض كلاسيكي مناسب للمناسبات الرسمية",
        "price": 299,
        "image": "https://images.unsplash.com/photo-1598033129183-c4f50c736f10",
        "category": "قمصان",
        "tags": ["رسمي", "كلاسيكي", "أبيض"]
    },
    {
        "id": "2",
        "name": "بنطلون جينز أزرق",
        "description": "بنطلون جينز أزرق عصري مناسب للإطلالات اليومية",
        "price": 399,
        "image": "https://images.unsplash.com/photo-1542272604-787c3835535d",
        "category": "بناطيل",
        "tags": ["عصري", "كاجوال", "أزرق"]
    },
    {
        "id": "3",
        "name": "حذاء رياضي أسود",
        "description": "حذاء رياضي أسود مريح ومناسب للاستخدام اليومي",
        "price": 499,
        "image": "https://images.unsplash.com/photo-1491553895911-0055eca6402d",
        "category": "أحذية",
        "tags": ["رياضي", "أسود", "مريح"]
    },
    {
        "id": "4",
        "name": "سترة صوفية رمادية",
        "description": "سترة صوفية رمادية دافئة ومناسبة لفصل الشتاء",
        "price": 599,
        "image": "https://images.unsplash.com/photo-1591047139829-d91aecb6caea",
        "category": "سترات",
        "tags": ["شتوي", "رمادي", "دافئ"]
    },
    {
        "id": "5",
        "name": "تيشيرت أسود بسيط",
        "description": "تيشيرت أسود بسيط مناسب للإطلالات اليومية",
        "price": 199,
        "image": "https://images.unsplash.com/photo-1503341504253-dff4815485f1",
        "category": "تيشيرتات",
        "tags": ["كاجوال", "أسود", "بسيط"]
    }
]

@app.route('/')
def index():
    return jsonify({
        "message": "مرحباً بك في واجهة برمجة تطبيقات موضة AI",
        "status": "متصل",
        "version": "1.0.0"
    })

@app.route('/api/products', methods=['GET'])
def get_products():
    return jsonify(products)

@app.route('/api/products/<product_id>', methods=['GET'])
def get_product(product_id):
    product = next((p for p in products if p["id"] == product_id), None)
    if product:
        return jsonify(product)
    return jsonify({"error": "المنتج غير موجود"}), 404

@app.route('/api/products/search', methods=['GET'])
def search_products():
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify(products)
    
    results = [p for p in products if 
               query in p["name"].lower() or 
               query in p["description"].lower() or 
               any(query in tag.lower() for tag in p["tags"])]
    
    return jsonify(results)

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    user_id = request.args.get('user_id')
    
    # في حالة وجود مستخدم، نقدم توصيات مخصصة
    if user_id and user_id in [u["id"] for u in users.values()]:
        user = next((u for u in users.values() if u["id"] == user_id), None)
        user_preferences = user.get("preferences", [])
        
        # محاكاة لخوارزمية توصيات ذكية
        recommended = [p for p in products if 
                      any(pref.lower() in p["name"].lower() or 
                          pref.lower() in p["description"].lower() or
                          any(pref.lower() in tag.lower() for tag in p["tags"]) 
                          for pref in user_preferences)]
        
        # إذا لم نجد توصيات كافية، نضيف بعض المنتجات العشوائية
        if len(recommended) < 3:
            remaining = [p for p in products if p not in recommended]
            recommended.extend(random.sample(remaining, min(3 - len(recommended), len(remaining))))
        
        return jsonify(recommended)
    
    # في حالة عدم وجود مستخدم، نقدم منتجات عشوائية
    return jsonify(random.sample(products, min(3, len(products))))

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if email in users and users[email]["password"] == password:
        user = users[email].copy()
        user.pop('password', None)  # لا نرسل كلمة المرور في الاستجابة
        return jsonify({
            "success": True,
            "message": "تم تسجيل الدخول بنجاح",
            "user": user
        })
    
    return jsonify({
        "success": False,
        "message": "البريد الإلكتروني أو كلمة المرور غير صحيحة"
    }), 401

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    
    if email in users:
        return jsonify({
            "success": False,
            "message": "البريد الإلكتروني مستخدم بالفعل"
        }), 400
    
    user_id = str(len(users) + 1)
    users[email] = {
        "id": user_id,
        "email": email,
        "password": password,
        "name": name,
        "preferences": []
    }
    
    user = users[email].copy()
    user.pop('password', None)  # لا نرسل كلمة المرور في الاستجابة
    
    return jsonify({
        "success": True,
        "message": "تم إنشاء الحساب بنجاح",
        "user": user
    })

@app.route('/api/auth/profile', methods=['GET'])
def get_profile():
    email = request.args.get('email')
    
    if email and email in users:
        user = users[email].copy()
        user.pop('password', None)  # لا نرسل كلمة المرور في الاستجابة
        return jsonify({
            "success": True,
            "user": user
        })
    
    return jsonify({
        "success": False,
        "message": "المستخدم غير موجود"
    }), 404

@app.route('/api/auth/profile', methods=['PUT'])
def update_profile():
    data = request.get_json()
    email = data.get('email')
    
    if email and email in users:
        # تحديث البيانات المسموح بها فقط
        if 'name' in data:
            users[email]['name'] = data['name']
        if 'preferences' in data:
            users[email]['preferences'] = data['preferences']
        
        user = users[email].copy()
        user.pop('password', None)  # لا نرسل كلمة المرور في الاستجابة
        
        return jsonify({
            "success": True,
            "message": "تم تحديث الملف الشخصي بنجاح",
            "user": user
        })
    
    return jsonify({
        "success": False,
        "message": "المستخدم غير موجود"
    }), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
