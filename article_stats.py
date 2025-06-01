from datetime import datetime
from src import db

class ArticleStats(db.Model):
    __tablename__ = 'article_stats'
    
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), primary_key=True)
    views = db.Column(db.Integer, default=0)
    shares = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ArticleStats for article {self.article_id}>'
