# models/Category.py
from datetime import datetime
from bson import ObjectId

class Category:
    """
    Category model for MongoDB
    """
    
    required_fields = ['name', 'user_id']
    
    def __init__(self, name, user_id=None, description=None, color=None, icon=None, 
                 created_at=None, _id=None, **kwargs):
        self._id = _id or ObjectId()
        self.name = name
        self.user_id = ObjectId(user_id) if user_id and isinstance(user_id, str) else user_id
        self.description = description or ""
        self.color = color or "#3498db"  # Default blue color
        self.icon = icon or "tag"  # Default icon name
        self.created_at = created_at or datetime.utcnow()
        
        # Add any additional fields from kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a Category instance from a dictionary, typically from MongoDB
        """
        # Handle _id conversion
        if '_id' in data and isinstance(data['_id'], str):
            data['_id'] = ObjectId(data['_id'])
            
        # Handle user_id conversion
        if 'user_id' in data and isinstance(data['user_id'], str):
            data['user_id'] = ObjectId(data['user_id'])
            
        # Convert created_at string to datetime if needed
        if 'created_at' in data and isinstance(data['created_at'], str):
            try:
                data['created_at'] = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
            except ValueError:
                data['created_at'] = datetime.utcnow()
            
        return cls(**data)
    
    def to_dict(self):
        """
        Convert the Category instance to a dictionary for MongoDB storage
        """
        category_dict = {
            '_id': self._id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'icon': self.icon,
            'created_at': self.created_at
        }
        
        # Include user_id if it exists
        if hasattr(self, 'user_id') and self.user_id is not None:
            category_dict['user_id'] = self.user_id
        
        # Include any additional attributes that may have been added
        for key, value in self.__dict__.items():
            if key not in category_dict and not key.startswith('_'):
                category_dict[key] = value
                
        return category_dict
    
    @staticmethod
    def validate(category_data):
        """
        Validate category data before creating or updating a category
        Returns (is_valid, errors)
        """
        errors = {}
        
        # Check required fields
        for field in Category.required_fields:
            if field not in category_data or not category_data[field]:
                errors[field] = f"{field} is required"
        
        # Validate name length
        if 'name' in category_data and category_data['name']:
            if len(category_data['name']) < 2:
                errors['name'] = "Name must be at least 2 characters long"
                
        return len(errors) == 0, errors