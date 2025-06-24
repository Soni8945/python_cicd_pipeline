from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os
import datetime # Import datetime for handling timestamps

app = Flask(__name__)

# --- Database Configuration for PostgreSQL ---
# It's highly recommended to use environment variables for sensitive data like
# database credentials in a production environment.
# For demonstration, we'll hardcode them, but be cautious with this in real apps.

DB_USER = os.environ.get('DB_USER', 'postgres') # Default to 'postgres' if not set
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'mysecretpassword') # Default password
DB_HOST = os.environ.get('DB_HOST', 'localhost') # Default to 'localhost'
DB_PORT = os.environ.get('DB_PORT', '5432') # Default PostgreSQL port
DB_NAME = os.environ.get('DB_NAME', 'my_app_db') # Your database name

# Construct the PostgreSQL connection URI
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Disable tracking modifications for better performance

db = SQLAlchemy(app)

# --- Database Model ---
class Item(db.Model):
    # __tablename__ is optional, by default SQLAlchemy uses lowercase class name 'item'
    # write exect table name as in the database
    __tablename__ = 'items'  

    # match all the column as in the table 

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200))
    # Using db.DateTime with default=db.func.now() for PostgreSQL's timestamp
    created_at = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f'(Item {self.name})'
    
    

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            # Format datetime objects to ISO 8601 string for JSON
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# --- API Endpoints ---

@app.route('/')
def home():
    """Simple home endpoint."""
    return "Welcome to the PostgreSQL Data Management Backend! Use /items endpoint."

# --- INSERT (Create a new item) ---
@app.route('/items', methods=['POST'])
def create_item():
    """
    Creates a new item in the database.
    Requires JSON payload: {"name": "New Item Name", "description": "Description of new item"}
    """
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid JSON data provided"}), 400
    if 'name' not in data:
        return jsonify({"message": "Name is required"}), 400

    new_item = Item(name=data['name'], description=data.get('description'))

    try: 
        db.session.add(new_item)
        db.session.commit()
        return jsonify({"message": "Item created successfully", "item": new_item.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error creating item", "error": str(e)}), 500

# --- FETCH ALL (Read all items) ---
@app.route('/items', methods=['GET'])
def get_all_items():
    """
    Fetches and returns all items from the database.
    """
    items = Item.query.all()
    return jsonify([item.to_dict() for item in items]), 200

# --- FETCH SINGLE (Read a single item by ID) ---
@app.route('/items/<int:item_id>', methods=['GET'])
def get_single_item(item_id):
    """
    Fetches and returns a single item by its ID.
    """
    item = Item.query.get(item_id)
    if item:
        return jsonify(item.to_dict()), 200
    return jsonify({"message": f"Item with ID {item_id} not found"}), 404

# --- UPDATE (Modify an existing item) ---
# @app.route('/items/<int:item_id>', methods=['PUT'])
# def update_item(item_id):
#     """
#     Updates an existing item in the database.
#     Requires JSON payload: {"name": "Updated Name", "description": "Updated Description"}
#     """
#     item = db.session.get(Item, item_id) # Newer SQLAlchemy 1.4+ way to get by primary key
#     if not item:
#         return jsonify({"message": f"Item with ID {item_id} not found"}), 404

#     data = request.get_json()
#     if not data:
#         return jsonify({"message": "Invalid JSON data provided"}), 400

#     try:
#         if 'name' in data:
#             item.name = data['name']
#         if 'description' in data:
#             item.description = data['description']

#         db.session.commit()
#         return jsonify({"message": "Item updated successfully", "item": item.to_dict()}), 200
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"message": "Error updating item", "error": str(e)}), 500

# --- DELETE (Remove an item) ---
@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """
    Deletes an item from the database by its ID.
    """
    item = db.session.get(Item, item_id)
    if not item:
        return jsonify({"message": f"Item with ID {item_id} not found"}), 404

    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": "Item deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error deleting item", "error": str(e)}), 500


# --- Running the app ---
if __name__ == '__main__':
    # Ensure database tables are created within the application context
    with app.app_context():
        print("Attempting to connect to PostgreSQL and create tables...")
        try:
            # db.create_all() # Creates tables based on models
            # print("PostgreSQL tables checked/created successfully.")

            # Optional: Add some initial data if the database is empty
            if not Item.query.first():
                print("Database is empty. Adding some sample data...")
                sample_items = [
                    Item(name="Desktop PC", description="Powerful computer for home or office."),
                    Item(name="Monitor", description="High-resolution display."),
                    Item(name="Webcam", description="Device for video conferencing.")
                ]
                db.session.add_all(sample_items)
                db.session.commit()
                print("Sample data added.")
        except Exception as e:
            print(f"Error connecting to PostgreSQL or creating tables: {e}")
            print("Please ensure your PostgreSQL server is running and database credentials are correct.")
            # Exit or handle the error appropriately if DB connection is critical
            exit(1) # Exit if we can't connect to the database on startup

    app.run(debug=True, host='0.0.0.0', port=5000)
