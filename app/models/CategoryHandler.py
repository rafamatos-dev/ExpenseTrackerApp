# models/CategoryHandler.py
from app.database import get_db
from app.models.Category import Category
from bson import ObjectId
from pymongo.errors import DuplicateKeyError, PyMongoError

class CategoryHandler:
    """
    Repository class for handling Category document operations in MongoDB
    """
    
    def __init__(self):
        self.db = get_db().db
        self.collection = self.db.categories
        
        # Ensure indexes for performance and constraints
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Create necessary indexes for the categories collection"""
        # Compound index to ensure name uniqueness per user
        self.collection.create_index([('name', 1), ('user_id', 1)], unique=True)
        # Index by user_id for faster querying
        self.collection.create_index('user_id')
    
    def find_by_id(self, category_id):
        """Find a category by its ID"""
        if isinstance(category_id, str):
            category_id = ObjectId(category_id)
            
        category_data = self.collection.find_one({'_id': category_id})
        if category_data:
            return Category.from_dict(category_data)
        return None
    
    def find_by_user(self, user_id, skip=0, limit=100, sort_by='name', sort_dir=1):
        """Find all categories for a user with pagination"""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
            
        # Query for user's categories
        cursor = self.collection.find({'user_id': user_id})
        
        # Apply sorting
        cursor = cursor.sort(sort_by, sort_dir)
        
        # Apply pagination
        total_count = self.collection.count_documents({'user_id': user_id})
        cursor = cursor.skip(skip).limit(limit)
        
        # Convert to Category objects
        categories = [Category.from_dict(category_data) for category_data in cursor]
        
        return {
            'categories': categories,
            'total': total_count,
            'skip': skip,
            'limit': limit
        }
    
    def create(self, category_data):
        """
        Create a new category
        Returns (success, result)
        """
        # Validate category data
        is_valid, errors = Category.validate(category_data)
        if not is_valid:
            return False, errors
        
        # Create category instance
        category = Category(**category_data)
        
        try:
            # Insert into database
            result = self.collection.insert_one(category.to_dict())
            category._id = result.inserted_id
            return True, category
        except DuplicateKeyError:
            return False, {'error': 'Category with this name already exists for this user'}
        except PyMongoError as e:
            return False, {'error': str(e)}
    
    def update(self, category_id, update_data):
        """
        Update a category
        Returns (success, result)
        """
        if isinstance(category_id, str):
            category_id = ObjectId(category_id)
            
        # Remove _id from updates if present
        update_data.pop('_id', None)
        
        try:
            result = self.collection.update_one(
                {'_id': category_id},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                return True, self.find_by_id(category_id)
            return False, {'error': 'Category not found or no changes made'}
        except DuplicateKeyError:
            return False, {'error': 'Category with this name already exists for this user'}
        except PyMongoError as e:
            return False, {'error': str(e)}
    
    def delete(self, category_id):
        """Delete a category by its ID"""
        if isinstance(category_id, str):
            category_id = ObjectId(category_id)
            
        # Check if category is being used by any expenses first
        # This would require access to the expenses collection
        # For now, we'll assume the caller has handled this check
            
        result = self.collection.delete_one({'_id': category_id})
        return result.deleted_count > 0
    
    def create_default_categories(self, user_id):
        """
        Create default categories for a new user
        Returns number of categories created
        """
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
            
        # Define default categories
        default_categories = [
            {
                'name': 'Food & Dining',
                'description': 'Restaurants, groceries, and food delivery',
                'color': '#FF5733',
                'icon': 'restaurant'
            },
            {
                'name': 'Transportation',
                'description': 'Public transit, gas, and vehicle maintenance',
                'color': '#3498DB',
                'icon': 'directions_car'
            },
            {
                'name': 'Housing',
                'description': 'Rent, mortgage, and home maintenance',
                'color': '#2ECC71',
                'icon': 'home'
            },
            {
                'name': 'Entertainment',
                'description': 'Movies, concerts, and other entertainment',
                'color': '#9B59B6',
                'icon': 'movie'
            },
            {
                'name': 'Shopping',
                'description': 'Clothing, electronics, and other retail purchases',
                'color': '#F39C12',
                'icon': 'shopping_cart'
            },
            {
                'name': 'Utilities',
                'description': 'Electricity, water, internet, and phone bills',
                'color': '#1ABC9C',
                'icon': 'power'
            },
            {
                'name': 'Healthcare',
                'description': 'Medical appointments, medications, and insurance',
                'color': '#E74C3C',
                'icon': 'local_hospital'
            },
            {
                'name': 'Travel',
                'description': 'Flights, hotels, and vacation expenses',
                'color': '#34495E',
                'icon': 'flight'
            },
            {
                'name': 'Personal Care',
                'description': 'Haircuts, gym memberships, and personal care items',
                'color': '#D35400',
                'icon': 'spa'
            },
            {
                'name': 'Other',
                'description': 'Miscellaneous expenses',
                'color': '#7F8C8D',
                'icon': 'more_horiz'
            }
        ]
        
        # Add user_id to each category
        for category in default_categories:
            category['user_id'] = user_id
            
        # Create all categories and track success
        created_count = 0
        for category_data in default_categories:
            try:
                category = Category(**category_data)
                self.collection.insert_one(category.to_dict())
                created_count += 1
            except DuplicateKeyError:
                # Skip if category already exists
                pass
            except Exception:
                # Skip on any other error
                pass
                
        return created_count