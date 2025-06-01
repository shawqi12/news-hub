from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from src import db
from src.models.article import Article
from src.models.comment import Comment
from src.models.article_stats import ArticleStats

articles_bp = Blueprint('articles', __name__)

@articles_bp.route('/<string:slug>')
def show(slug):
    """عرض مقال محدد"""
    article = Article.query.filter_by(slug=slug, status='published').first_or_404()
    
    # زيادة عدد المشاهدات
    if not article.stats:
        stats = ArticleStats(article_id=article.id)
        db.session.add(stats)
    else:
        article.stats.views += 1
    
    article.views_count += 1
    db.session.commit()
    
    # الحصول على التعليقات
    comments = Comment.query.filter_by(article_id=article.id, parent_id=None, status='approved').order_by(Comment.created_at.desc()).all()
    
    # الحصول على المقالات ذات الصلة
    related_articles = Article.query.filter(
        Article.category_id == article.category_id,
        Article.id != article.id,
        Article.status == 'published'
    ).order_by(Article.published_at.desc()).limit(4).all()
    
    return render_template('articles/show.html', 
                          article=article, 
                          comments=comments, 
                          related_articles=related_articles)

@articles_bp.route('/<string:slug>/comment', methods=['POST'])
def add_comment(slug):
    """إضافة تعليق على مقال"""
    article = Article.query.filter_by(slug=slug).first_or_404()
    
    content = request.form.get('content')
    parent_id = request.form.get('parent_id')
    
    if not content:
        flash('محتوى التعليق مطلوب', 'danger')
        return redirect(url_for('articles.show', slug=slug))
    
    if current_user.is_authenticated:
        comment = Comment(
            article_id=article.id,
            user_id=current_user.id,
            content=content,
            parent_id=parent_id if parent_id else None,
            status='approved' if current_user.role in ['admin', 'editor'] else 'pending'
        )
    else:
        author_name = request.form.get('author_name')
        author_email = request.form.get('author_email')
        
        if not author_name or not author_email:
            flash('الاسم والبريد الإلكتروني مطلوبان للتعليق كزائر', 'danger')
            return redirect(url_for('articles.show', slug=slug))
        
        comment = Comment(
            article_id=article.id,
            content=content,
            author_name=author_name,
            author_email=author_email,
            parent_id=parent_id if parent_id else None,
            status='pending'
        )
    
    db.session.add(comment)
    
    # تحديث عدد التعليقات في الإحصائيات
    if article.stats:
        article.stats.comments_count += 1
    
    db.session.commit()
    
    if comment.status == 'pending':
        flash('تم إرسال تعليقك وسيتم مراجعته قبل النشر', 'info')
    else:
        flash('تم إضافة تعليقك بنجاح', 'success')
    
    return redirect(url_for('articles.show', slug=slug))

@articles_bp.route('/<string:slug>/share/<string:platform>')
def share(slug, platform):
    """مشاركة المقال على وسائل التواصل الاجتماعي"""
    article = Article.query.filter_by(slug=slug).first_or_404()
    
    # زيادة عدد المشاركات
    if article.stats:
        article.stats.shares += 1
        db.session.commit()
    
    # إعادة توجيه إلى منصة المشاركة المناسبة
    article_url = url_for('articles.show', slug=slug, _external=True)
    
    if platform == 'facebook':
        share_url = f"https://www.facebook.com/sharer/sharer.php?u={article_url}"
    elif platform == 'twitter':
        share_url = f"https://twitter.com/intent/tweet?url={article_url}&text={article.title}"
    elif platform == 'whatsapp':
        share_url = f"https://api.whatsapp.com/send?text={article.title} {article_url}"
    else:
        abort(404)
    
    return redirect(share_url)
