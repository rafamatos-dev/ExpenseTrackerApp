# models/user.py
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId

class User:
    """
    User model for MongoDB
    """
    
    required_fields = ['username', 'email', 'password']
    
    def __init__(self, username, email, password=None, first_name=None, 
                 last_name=None, created_at=None, _id=None, **kwargs):
        self._id = _id or ObjectId()
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password) if password else None
        self.first_name = first_name
        self.last_name = last_name
        self.created_at = created_at or datetime.utcnow()
        
        # Add any additional fields from kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a User instance from a dictionary, typically from MongoDB
        """
        # If password_hash exists, don't try to hash it again
        if 'password_hash' in data:
            data.pop('password', None)  # Remove plain password if it exists
        
        # Handle _id conversion
        if '_id' in data and isinstance(data['_id'], str):
            data['_id'] = ObjectId(data['_id'])
            
        return cls(**data)
    
    def to_dict(self, include_private=False):
        """
        Convert the User instance to a dictionary for MongoDB storage
        
        Args:
            include_private: Whether to include private fields like password_hash
        """
        user_dict = {
            '_id': self._id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'created_at': self.created_at
        }
        
        # Include password hash only if specifically requested
        if include_private and hasattr(self, 'password_hash'):
            user_dict['password_hash'] = self.password_hash
            
        # Include any additional attributes that may have been added
        for key, value in self.__dict__.items():
            if key not in user_dict and not key.startswith('_'):
                user_dict[key] = value
                
        return user_dict
    
    def check_password(self, password):
        """
        Verify the password against the stored hash
        """
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def set_password(self, password):
        """
        Set a new password
        """
        self.password_hash = generate_password_hash(password)
        
    @staticmethod
    def validate(user_data):
        """
        Validate user data before creating or updating a user
        Returns (is_valid, errors)
        """
        errors = {}
        
        # Check required fields
        for field in User.required_fields:
            if field not in user_data or not user_data[field]:
                errors[field] = f"{field} is required"
        
        # Validate email format (simple check)
        if 'email' in user_data and user_data['email']:
            if '@' not in user_data['email'] or '.' not in user_data['email']:
                errors['email'] = "Invalid email format"
        
        # Validate username (alphanumeric and underscore only)
        if 'username' in user_data and user_data['username']:
            if not all(c.isalnum() or c == '_' for c in user_data['username']):
                errors['username'] = "Username must contain only letters, numbers, and underscores"
        
        # Validate password strength
        if 'password' in user_data and user_data['password']:
            if len(user_data['password']) < 8:
                errors['password'] = "Password must be at least 8 characters long"
        
        return len(errors) == 0, errors