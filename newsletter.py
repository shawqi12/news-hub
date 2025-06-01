from datetime import datetime
from src import db

class NewsletterSubscriber(db.Model):
    __tablename__ = 'newsletter_subscribers'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(64), nullable=True)
    subscribed_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    categories = db.Column(db.Text, nullable=True)  # مخزنة كسلسلة JSON
    
    def __repr__(self):
        return f'<NewsletterSubscriber {self.email}>'
