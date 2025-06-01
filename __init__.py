from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os

# تهيئة قاعدة البيانات
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # إعدادات التطبيق
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_testing')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///news_website.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # تهيئة الإضافات
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة'
    
    # استيراد النماذج
    from src.models.user import User
    from src.models.category import Category
    from src.models.article import Article
    from src.models.tag import Tag
    from src.models.comment import Comment
    from src.models.media import Media
    from src.models.article_stats import ArticleStats
    from src.models.newsletter import NewsletterSubscriber
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # تسجيل المسارات
    from src.routes.main import main_bp
    from src.routes.auth import auth_bp
    from src.routes.articles import articles_bp
    from src.routes.admin import admin_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(articles_bp, url_prefix='/articles')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    return app
