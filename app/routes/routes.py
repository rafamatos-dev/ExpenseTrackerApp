# routes.py - All application routes
from flask import render_template, request, jsonify

def register_routes(app, mongo):
    # Basic route
    @app.route('/')
    def index():
        return render_template('index.html')

    # Route to get all items from a collection
    @app.route('/api/items', methods=['GET'])
    def get_items():
        items = list(mongo.db.items.find({}, {'_id': False}))
        return jsonify(items)

    # Route to add a new item
    @app.route('/api/items', methods=['POST'])
    def add_item():
        item = request.json
        mongo.db.items.insert_one(item)
        return jsonify({"message": "Item added successfully"})

    # Route to get a specific item
    @app.route('/api/items/<item_id>', methods=['GET'])
    def get_item(item_id):
        item = mongo.db.items.find_one({"id": item_id}, {'_id': False})
        if item:
            return jsonify(item)
        return jsonify({"error": "Item not found"}), 404

    # Route to update an item
    @app.route('/api/items/<item_id>', methods=['PUT'])
    def update_item(item_id):
        update_data = request.json
        mongo.db.items.update_one({"id": item_id}, {"$set": update_data})
        return jsonify({"message": "Item updated successfully"})

    # Route to delete an item
    @app.route('/api/items/<item_id>', methods=['DELETE'])
    def delete_item(item_id):
        mongo.db.items.delete_one({"id": item_id})
        return jsonify({"message": "Item deleted successfully"})