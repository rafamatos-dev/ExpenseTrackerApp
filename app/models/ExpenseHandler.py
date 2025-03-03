# models/ExpenseHandler.py
from app.database import get_db
from app.models.Expense import Expense
from bson import ObjectId
from datetime import datetime
from pymongo.errors import PyMongoError

class ExpenseHandler:
    """
    Repository class for handling Expense document operations in MongoDB
    """
    
    def __init__(self):
        self.db = get_db().db
        self.collection = self.db.expenses
        
        # Ensure indexes for performance
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Create necessary indexes for the expenses collection"""
        # Index by user_id for faster querying of a user's expenses
        self.collection.create_index('user_id')
        # Index by category_id for faster category filtering
        self.collection.create_index('category_id')
        # Compound index for date-based queries per user
        self.collection.create_index([('user_id', 1), ('date', -1)])
    
    def find_by_id(self, expense_id):
        """Find an expense by its ID"""
        if isinstance(expense_id, str):
            expense_id = ObjectId(expense_id)
            
        expense_data = self.collection.find_one({'_id': expense_id})
        if expense_data:
            return Expense.from_dict(expense_data)
        return None
    
    def find_by_user(self, user_id, skip=0, limit=50, sort_by='date', sort_dir=-1, 
                     start_date=None, end_date=None, category_id=None):
        """
        Find all expenses for a user with optional filtering and pagination
        """
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
            
        # Build query
        query = {'user_id': user_id}
        
        # Add date range filter if provided
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query['$gte'] = start_date
            if end_date:
                date_query['$lte'] = end_date
                
            if date_query:
                query['date'] = date_query
                
        # Add category filter if provided
        if category_id:
            if isinstance(category_id, str):
                category_id = ObjectId(category_id)
            query['category_id'] = category_id
            
        # Execute query with pagination
        cursor = self.collection.find(query)
        
        # Apply sorting
        cursor = cursor.sort(sort_by, sort_dir)
        
        # Apply pagination
        total_count = self.collection.count_documents(query)
        cursor = cursor.skip(skip).limit(limit)
        
        # Convert to Expense objects
        expenses = [Expense.from_dict(expense_data) for expense_data in cursor]
        
        return {
            'expenses': expenses,
            'total': total_count,
            'skip': skip,
            'limit': limit
        }
    
    def create(self, expense_data):
        """
        Create a new expense
        Returns (success, result)
        """
        # Validate expense data
        is_valid, errors = Expense.validate(expense_data)
        if not is_valid:
            return False, errors
        
        # Set timestamps
        now = datetime.utcnow()
        if 'created_at' not in expense_data:
            expense_data['created_at'] = now
        if 'updated_at' not in expense_data:
            expense_data['updated_at'] = now
        
        # Create expense instance
        expense = Expense(**expense_data)
        
        try:
            # Insert into database
            result = self.collection.insert_one(expense.to_dict())
            expense._id = result.inserted_id
            return True, expense
        except PyMongoError as e:
            return False, {'error': str(e)}
    
    def update(self, expense_id, update_data):
        """
        Update an expense
        Returns (success, result)
        """
        if isinstance(expense_id, str):
            expense_id = ObjectId(expense_id)
            
        # Get the existing expense
        expense = self.find_by_id(expense_id)
        if not expense:
            return False, {'error': 'Expense not found'}
            
        # Set updated timestamp
        update_data['updated_at'] = datetime.utcnow()
        
        # Handle category_id conversion if string
        if 'category_id' in update_data and isinstance(update_data['category_id'], str):
            update_data['category_id'] = ObjectId(update_data['category_id'])
            
        try:
            # Update the expense object
            expense.update(update_data)
            
            # Update in database
            result = self.collection.update_one(
                {'_id': expense_id},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                return True, expense
            return False, {'error': 'No changes made'}
        except PyMongoError as e:
            return False, {'error': str(e)}
    
    def delete(self, expense_id):
        """Delete an expense by its ID"""
        if isinstance(expense_id, str):
            expense_id = ObjectId(expense_id)
            
        result = self.collection.delete_one({'_id': expense_id})
        return result.deleted_count > 0
    
    def get_summary_by_category(self, user_id, start_date=None, end_date=None):
        """
        Get a summary of expenses grouped by category
        """
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
            
        # Build match query
        match_query = {'user_id': user_id}
        
        # Add date range filter if provided
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query['$gte'] = start_date
            if end_date:
                date_query['$lte'] = end_date
                
            if date_query:
                match_query['date'] = date_query
        
        # Aggregation pipeline
        pipeline = [
            {'$match': match_query},
            {'$group': {
                '_id': '$category_id',
                'total': {'$sum': '$amount'},
                'count': {'$sum': 1}
            }},
            {'$sort': {'total': -1}}
        ]
        
        # Execute aggregation
        result = list(self.collection.aggregate(pipeline))
        
        return result
    
    def get_summary_by_month(self, user_id, year=None):
        """
        Get a summary of expenses grouped by month for a specific year
        """
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
            
        # Set default year to current year if not provided
        if not year:
            year = datetime.utcnow().year
            
        # Build match query
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31, 23, 59, 59)
        
        match_query = {
            'user_id': user_id,
            'date': {
                '$gte': start_date,
                '$lte': end_date
            }
        }
        
        # Aggregation pipeline
        pipeline = [
            {'$match': match_query},
            {'$group': {
                '_id': {'$month': '$date'},
                'total': {'$sum': '$amount'},
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id': 1}}
        ]
        
        # Execute aggregation
        result = list(self.collection.aggregate(pipeline))
        
        # Format result with month names
        month_names = ['January', 'February', 'March', 'April', 'May', 'June', 
                       'July', 'August', 'September', 'October', 'November', 'December']
        
        formatted_result = []
        for item in result:
            month_index = item['_id'] - 1  # MongoDB month is 1-indexed
            formatted_result.append({
                'month': month_index + 1,
                'month_name': month_names[month_index],
                'total': item['total'],
                'count': item['count']
            })
            
        return formatted_result
    
    def get_summary_by_payment_method(self, user_id, start_date=None, end_date=None):
        """
        Get a summary of expenses grouped by payment method
        """
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
            
        # Build match query
        match_query = {'user_id': user_id}
        
        # Add date range filter if provided
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query['$gte'] = start_date
            if end_date:
                date_query['$lte'] = end_date
                
            if date_query:
                match_query['date'] = date_query
        
        # Aggregation pipeline
        pipeline = [
            {'$match': match_query},
            {'$group': {
                '_id': '$payment_method',
                'total': {'$sum': '$amount'},
                'count': {'$sum': 1}
            }},
            {'$sort': {'total': -1}}
        ]
        
        # Execute aggregation
        result = list(self.collection.aggregate(pipeline))
        
        return result