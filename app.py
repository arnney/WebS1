from flask import Flask, request, jsonify
from flask_pymongo import PyMongo, ObjectId
from flasgger import Swagger
from bson.errors import InvalidId


app = Flask(__name__)

app.config["MONGO_URI"] = 'mongodb://mongo:27017/SupplementStore'
mongo = PyMongo(app)


swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Supplement Store API",
        "description": "API for managing a supplement store",
        "version": "1.0"
    }
}
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/swagger/"
}
swagger = Swagger(app, template=swagger_template, config=swagger_config)


initial_brands = [
    {"name": "Brand A", "country": "Japan"},
    {"name": "Brand B", "country": "Turkey"},
]

initial_supplements = [
    {"name": "SupplementA", "description": "For Neurological functions", "brand_name": "Brand A", "price": 4.99},
    {"name": "SupplementB", "description": "Boosting muscle recovery", "brand_name": "Brand B", "price": 10.99},
    {"name": "SupplementC", "description": "Mental clarity", "brand_name": "Brand B", "price": 9.99},
]


def serialize(doc):
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc[key] = str(value)
    if '_id' in doc:
        doc['id'] = doc.pop('_id')
    return doc


def initialize_database():
    if mongo.db.brands.count_documents({}) == 0:
        mongo.db.brands.insert_many(initial_brands)

    if mongo.db.supplements.count_documents({}) == 0:
        for supplement in initial_supplements:
            brand = mongo.db.brands.find_one({"name": supplement["brand_name"]})
            if brand:
                supplement_data = {
                    "name": supplement["name"],
                    "description": supplement["description"],
                    "brand_id": brand["_id"],
                    "price": supplement["price"]
                }
                mongo.db.supplements.insert_one(supplement_data)

@app.route('/brands', methods=['GET'])
def get_brands():
    """
    file: docs/get_brands.yml
    """
    brands = mongo.db.brands.find()
    return jsonify([serialize(brand) for brand in brands]), 200

@app.route('/brands', methods=['POST'])
def add_brand():
    """
    file: docs/add_brand.yml
    """
    data = request.json
    if not data.get('name') or not data.get('country'):
        return jsonify({'error': 'Missing name or country'}), 400
    existing_brand = mongo.db.brands.find_one({'name': data['name'], 'country': data['country']})
    if existing_brand:
        return jsonify({'error': 'Brand already exists'}), 409
    result = mongo.db.brands.insert_one(data)
    new_brand = mongo.db.brands.find_one({'_id': result.inserted_id})
    return jsonify(serialize(new_brand)), 201

@app.route('/brands/<brand_id>', methods=['PUT'])
def update_brand(brand_id):
    """
    file: docs/update_brand.yml
    """
    data = request.json
    result = mongo.db.brands.update_one({'_id': ObjectId(brand_id)}, {'$set': data})
    if result.matched_count:
        updated_brand = mongo.db.brands.find_one({'_id': ObjectId(brand_id)})
        return jsonify(serialize(updated_brand)), 200
    else:
        return jsonify({'error': 'Brand not found'}), 404

@app.route('/brands/<brand_id>', methods=['DELETE'])
def delete_brand(brand_id):
    """
    file: docs/delete_brand.yml
    """
    result = mongo.db.brands.delete_one({'_id': ObjectId(brand_id)})
    if result.deleted_count:
        return jsonify({'message': 'Brand deleted'}), 200
    else:
        return jsonify({'error': 'Brand not found'}), 404

# Supplements
@app.route('/supplements', methods=['GET'])
def get_supplements():
    """
    file: docs/get_supplements.yml
    """
    supplements = mongo.db.supplements.find()
    return jsonify([serialize(supplement) for supplement in supplements]), 200

@app.route('/supplements', methods=['POST'])
def add_supplement():
    """
    file: docs/add_supplement.yml
    """
    data = request.json
    if not data.get('name') or not data.get('description') or not data.get('brand_id') or not data.get('price'):
        return jsonify({'error': 'Missing name, description, brand_id, or price'}), 400
    try:
        brand_id = ObjectId(data['brand_id'])
    except InvalidId:
        return jsonify({'error': 'Invalid brand_id format'}), 400

    if not mongo.db.brands.find_one({'_id': brand_id}):
        return jsonify({'error': 'Brand not found'}), 404
    existing_supplement = mongo.db.supplements.find_one({
        'name': data['name'],
        'brand_id': brand_id
    })
    if existing_supplement:
        return jsonify({'error': 'Supplement already exists for this brand'}), 409

    data['brand_id'] = brand_id
    result = mongo.db.supplements.insert_one(data)
    new_supplement = mongo.db.supplements.find_one({'_id': result.inserted_id})
    return jsonify(serialize(new_supplement)), 201

@app.route('/supplements/<supplement_id>', methods=['PUT'])
def update_supplement(supplement_id):
    """
    file: docs/update_supplement.yml
    """
    data = request.json
    result = mongo.db.supplements.update_one({'_id': ObjectId(supplement_id)}, {'$set': data})
    if result.matched_count:
        updated_supplement = mongo.db.supplements.find_one({'_id': ObjectId(supplement_id)})
        return jsonify(serialize(updated_supplement)), 200
    else:
        return jsonify({'error': 'Supplement not found'}), 404

@app.route('/supplements/<supplement_id>', methods=['DELETE'])
def delete_supplement(supplement_id):
    """
    file: docs/delete_supplement.yml
    """
    result = mongo.db.supplements.delete_one({'_id': ObjectId(supplement_id)})
    if result.deleted_count:
        return jsonify({'message': 'Supplement deleted'}), 200
    else:
        return jsonify({'error': 'Supplement not found'}), 404

initialize_database()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
