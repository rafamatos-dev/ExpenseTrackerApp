# models/Expense.py
from datetime import datetime
from bson import ObjectId

class Expense:
    """
    Expense model for MongoDB
    """
    
    required_fields = ['amount', 'description', 'category_id', 'user_id', 'date']
    
    def __init__(self, amount, description, category_id, user_id, date=None, 
                 payment_method=None, created_at=None, updated_at=None, _id=None, **kwargs):
        self._id = _id or ObjectId()
        self.amount = float(amount)
        self.description = description
        self.category_id = ObjectId(category_id) if isinstance(category_id, str) else category_id
        self.user_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
        self.date = date or datetime.utcnow()
        self.payment_method = payment_method or "Cash"
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        
        # Add any additional fields from kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @classmethod
    def from_dict(cls, data):
        """
        Create an Expense instance from a dictionary, typically from MongoDB
        """
        # Handle _id conversion
        if '_id' in data and isinstance(data['_id'], str):
            data['_id'] = ObjectId(data['_id'])
            
        # Handle category_id conversion
        if 'category_id' in data and isinstance(data['category_id'], str):
            data['category_id'] = ObjectId(data['category_id'])
            
        # Handle user_id conversion
        if 'user_id' in data and isinstance(data['user_id'], str):
            data['user_id'] = ObjectId(data['user_id'])
            
        # Convert date string to datetime if needed
        if 'date' in data and isinstance(data['date'], str):
            try:
                data['date'] = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
            except ValueError:
                data['date'] = datetime.utcnow()
                
        # Convert created_at string to datetime if needed
        if 'created_at' in data and isinstance(data['created_at'], str):
            try:
                data['created_at'] = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
            except ValueError:
                data['created_at'] = datetime.utcnow()
                
        # Convert updated_at string to datetime if needed
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            try:
                data['updated_at'] = datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00'))
            except ValueError:
                data['updated_at'] = datetime.utcnow()
            
        return cls(**data)
    
    def to_dict(self):
        """
        Convert the Expense instance to a dictionary for MongoDB storage
        """
        expense_dict = {
            '_id': self._id,
            'amount': self.amount,
            'description': self.description,
            'category_id': self.category_id,
            'user_id': self.user_id,
            'date': self.date,
            'payment_method': self.payment_method,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
        # Include any additional attributes that may have been added
        for key, value in self.__dict__.items():
            if key not in expense_dict and not key.startswith('_'):
                expense_dict[key] = value
                
        return expense_dict
    
    def update(self, update_data):
        """
        Update the expense with new data
        """
        for key, value in update_data.items():
            if hasattr(self, key) and key != '_id':
                setattr(self, key, value)
        
        # Always update the updated_at timestamp
        self.updated_at = datetime.utcnow()
    
    @staticmethod
    def validate(expense_data):
        """
        Validate expense data before creating or updating an expense
        Returns (is_valid, errors)
        """
        errors = {}
        
        # Check required fields
        for field in Expense.required_fields:
            if field not in expense_data or expense_data[field] is None:
                errors[field] = f"{field} is required"
        
        # Validate amount is a number and positive
        if 'amount' in expense_data and expense_data['amount'] is not None:
            try:
                amount = float(expense_data['amount'])
                if amount <= 0:
                    errors['amount'] = "Amount must be positive"
            except ValueError:
                errors['amount'] = "Amount must be a number"
        
        return len(errors) == 0, errors