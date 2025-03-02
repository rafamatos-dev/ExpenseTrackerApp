from database import get_db
from models.User import User
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

class UserRepository:
    """
    Repository class for handling User document operations in MongoDB
    """
    
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.users
        
        # Ensure indexes for performance and constraints
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Create necessary indexes for the users collection"""
        # Username and email should be unique
        self.collection.create_index('username', unique=True)
        self.collection.create_index('email', unique=True)
    
    def find_by_id(self, user_id):
        """Find a user by their ID"""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
            
        user_data = self.collection.find_one({'_id': user_id})
        if user_data:
            return User.from_dict(user_data)
        return None
    
    def find_by_username(self, username):
        """Find a user by their username"""
        user_data = self.collection.find_one({'username': username})
        if user_data:
            return User.from_dict(user_data)
        return None
    
    def find_by_email(self, email):
        """Find a user by their email"""
        user_data = self.collection.find_one({'email': email})
        if user_data:
            return User.from_dict(user_data)
        return None
    
    def create(self, user_data):
        """
        Create a new user
        Returns (success, result)
        - If success is True, result is the created User
        - If success is False, result is the error message
        """
        # Validate user data
        is_valid, errors = User.validate(user_data)
        if not is_valid:
            return False, errors
        
        # Check if username or email already exists
        if self.find_by_username(user_data['username']):
            return False, {'username': 'Username already exists'}
        
        if self.find_by_email(user_data['email']):
            return False, {'email': 'Email already exists'}
        
        # Create user instance
        user = User(**user_data)
        
        try:
            # Insert into database
            result = self.collection.insert_one(user.to_dict(include_private=True))
            user._id = result.inserted_id
            return True, user
        except DuplicateKeyError:
            return False, {'error': 'User with this username or email already exists'}
        except Exception as e:
            return False, {'error': str(e)}
    
    def update(self, user_id, update_data):
        """
        Update a user's information
        Returns (success, result)
        """
        # Remove password from direct updates for security
        if 'password' in update_data:
            # Get the user to update their password properly
            user = self.find_by_id(user_id)
            if user:
                user.set_password(update_data['password'])
                update_data['password_hash'] = user.password_hash
            del update_data['password']
        
        # Remove _id from updates if present
        update_data.pop('_id', None)
        
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                return True, self.find_by_id(user_id)
            return False, {'error': 'User not found or no changes made'}
        except DuplicateKeyError:
            return False, {'error': 'Username or email already exists'}
        except Exception as e:
            return False, {'error': str(e)}
    
    def delete(self, user_id):
        """Delete a user by their ID"""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
            
        result = self.collection.delete_one({'_id': user_id})
        return result.deleted_count > 0
    
    def list_all(self, skip=0, limit=20, sort_by='username', sort_dir=1):
        """List all users with pagination"""
        cursor = self.collection.find({}, {'password_hash': 0})
        
        # Apply sorting
        cursor = cursor.sort(sort_by, sort_dir)
        
        # Apply pagination
        cursor = cursor.skip(skip).limit(limit)
        
        # Convert to User objects
        users = [User.from_dict(user_data) for user_data in cursor]
        
        # Get total count
        total_count = self.collection.count_documents({})
        
        return {
            'users': users,
            'total': total_count,
            'skip': skip,
            'limit': limit
        }