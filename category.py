from datetime import datetime
from src import db

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    slug = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(255), nullable=True)
    order = db.Column(db.Integer, default=0)
    
    # العلاقات
    articles = db.relationship('Article', backref='category', lazy='dynamic')
    
    def __repr__(self):
        return f'<Category {self.name}>'
