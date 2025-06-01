from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from src import db
from src.models.article import Article
from src.models.category import Category
from src.models.tag import Tag
from src.models.comment import Comment
from src.models.user import User
from werkzeug.utils import secure_filename
import os
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

# التحقق من صلاحيات المسؤول
def admin_required(view_func):
    @login_required
    def wrapped_view(*args, **kwargs):
        if current_user.role not in ['admin', 'editor']:
            abort(403)
        return view_func(*args, **kwargs)
    wrapped_view.__name__ = view_func.__name__
    return wrapped_view

@admin_bp.route('/')
@admin_required
def index():
    """لوحة التحكم الرئيسية"""
    articles_count = Article.query.count()
    comments_count = Comment.query.count()
    users_count = User.query.count()
    pending_comments = Comment.query.filter_by(status='pending').count()
    
    recent_articles = Article.query.order_by(Article.published_at.desc()).limit(5).all()
    
    return render_template('admin/index.html', 
                          articles_count=articles_count,
                          comments_count=comments_count,
                          users_count=users_count,
                          pending_comments=pending_comments,
                          recent_articles=recent_articles)

@admin_bp.route('/articles')
@admin_required
def articles():
    """إدارة المقالات"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'all')
    
    query = Article.query
    if status != 'all':
        query = query.filter_by(status=status)
    
    articles = query.order_by(Article.published_at.desc()).paginate(page=page, per_page=20)
    
    return render_template('admin/articles/index.html', articles=articles, current_status=status)

@admin_bp.route('/articles/create', methods=['GET', 'POST'])
@admin_required
def create_article():
    """إنشاء مقال جديد"""
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        summary = request.form.get('summary')
        category_id = request.form.get('category_id')
        status = request.form.get('status', 'draft')
        is_featured = True if request.form.get('is_featured') else False
        is_breaking = True if request.form.get('is_breaking') else False
        
        if not title or not content or not category_id:
            flash('جميع الحقول المطلوبة يجب ملؤها', 'danger')
            return redirect(url_for('admin.create_article'))
        
        # إنشاء slug من العنوان
        slug = title.lower().replace(' ', '-')
        
        # التحقق من عدم تكرار الـ slug
        existing_article = Article.query.filter_by(slug=slug).first()
        if existing_article:
            slug = f"{slug}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        article = Article(
            title=title,
            slug=slug,
            content=content,
            summary=summary,
            category_id=category_id,
            author_id=current_user.id,
            status=status,
            is_featured=is_featured,
            is_breaking=is_breaking
        )
        
        db.session.add(article)
        db.session.commit()
        
        flash('تم إنشاء المقال بنجاح', 'success')
        return redirect(url_for('admin.articles'))
    
    categories = Category.query.all()
    tags = Tag.query.all()
    
    return render_template('admin/articles/create.html', categories=categories, tags=tags)

@admin_bp.route('/articles/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_article(id):
    """تعديل مقال"""
    article = Article.query.get_or_404(id)
    
    if request.method == 'POST':
        article.title = request.form.get('title')
        article.content = request.form.get('content')
        article.summary = request.form.get('summary')
        article.category_id = request.form.get('category_id')
        article.status = request.form.get('status')
        article.is_featured = True if request.form.get('is_featured') else False
        article.is_breaking = True if request.form.get('is_breaking') else False
        article.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('تم تحديث المقال بنجاح', 'success')
        return redirect(url_for('admin.articles'))
    
    categories = Category.query.all()
    tags = Tag.query.all()
    
    return render_template('admin/articles/edit.html', article=article, categories=categories, tags=tags)

@admin_bp.route('/comments')
@admin_required
def comments():
    """إدارة التعليقات"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'all')
    
    query = Comment.query
    if status != 'all':
        query = query.filter_by(status=status)
    
    comments = query.order_by(Comment.created_at.desc()).paginate(page=page, per_page=20)
    
    return render_template('admin/comments/index.html', comments=comments, current_status=status)

@admin_bp.route('/comments/<int:id>/approve', methods=['POST'])
@admin_required
def approve_comment(id):
    """الموافقة على تعليق"""
    comment = Comment.query.get_or_404(id)
    comment.status = 'approved'
    db.session.commit()
    
    flash('تم الموافقة على التعليق بنجاح', 'success')
    return redirect(url_for('admin.comments'))

@admin_bp.route('/comments/<int:id>/reject', methods=['POST'])
@admin_required
def reject_comment(id):
    """رفض تعليق"""
    comment = Comment.query.get_or_404(id)
    comment.status = 'rejected'
    db.session.commit()
    
    flash('تم رفض التعليق بنجاح', 'success')
    return redirect(url_for('admin.comments'))

@admin_bp.route('/categories', methods=['GET', 'POST'])
@admin_required
def categories():
    """إدارة الأقسام"""
    if request.method == 'POST':
        name = request.form.get('name')
        slug = request.form.get('slug') or name.lower().replace(' ', '-')
        description = request.form.get('description')
        
        category = Category(name=name, slug=slug, description=description)
        db.session.add(category)
        db.session.commit()
        
        flash('تم إنشاء القسم بنجاح', 'success')
        return redirect(url_for('admin.categories'))
    
    categories = Category.query.order_by(Category.order).all()
    return render_template('admin/categories/index.html', categories=categories)

@admin_bp.route('/users')
@admin_required
def users():
    """إدارة المستخدمين"""
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(page=page, per_page=20)
    
    return render_template('admin/users/index.html', users=users)
