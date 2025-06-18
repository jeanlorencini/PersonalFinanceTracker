from app import db
from datetime import datetime
import hashlib

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'receita', 'despesa', 'transferencia'
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    unique_hash = db.Column(db.String(64), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    category = db.relationship('Category', backref='transactions')
    
    def __init__(self, date, description, amount, type, category_id=None):
        self.date = date
        self.description = description
        self.amount = amount
        self.type = type
        self.category_id = category_id
        # Generate unique hash for duplicate detection
        hash_string = f"{date.isoformat()}_{description}_{amount}"
        self.unique_hash = hashlib.md5(hash_string.encode()).hexdigest()
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'description': self.description,
            'amount': self.amount,
            'type': self.type,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'created_at': self.created_at.isoformat()
        }

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat()
        }
