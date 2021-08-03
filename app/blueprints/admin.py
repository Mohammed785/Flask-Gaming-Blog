from flask import Blueprint,redirect,url_for,flash,render_template
from app.extensions import db
from app.forms import ArticleForm,CategoryForm,TagsForm
from app.models import Article,Category,Tag,User
from app.utils import article_pic,redirect_back
from app.decorators import admin_required
from flask_login import current_user
from app.notifications import article_notification
admin = Blueprint('admin',__name__)



def send_notifications(article):
    users = User.query.all()
    for user in users:
        article_notification(article.id, user)
    return


@admin.route('/add/article',methods=['POST','GET'])
@admin_required
def add_article():
    form = ArticleForm()
    if form.validate_on_submit():
        article = Article(title=form.title.data, body=form.body.data,author=current_user)
        if form.review.data:
            article.review_score = form.review.data
            article.is_review = True
        article.article_pic = article_pic(form.pic.data)
        article.tags = form.tags.data
        article.category = form.categorys.data
        db.session.add(article)
        db.session.commit()
        send_notifications(article)
        flash('Article Added','success')
        return redirect(url_for('admin.add_article'))
    return render_template('admin/article.html',form=form)



@admin.route('/edit/article/<int:article_id>', methods=['POST', 'GET'])
@admin_required
def edit_article(article_id):
    article= Article.query.get_or_404(article_id)
    form= ArticleForm()
    if form.validate_on_submit():
        if form.review.data:
            article.review_score = form.review.data
            article.is_review = True
        else:
            article.review_score = None
            article.is_review = False
        if form.pic.data:
            article.article_pic = article_pic(form.pic.data)
        article.title= form.title.data
        article.body = form.body.data
        article.category = form.categorys.data
        article.tags = form.tags.data
        db.session.commit()
        flash('Article Updated','success')
        return redirect(url_for('routes.home'))
    form.title.data=article.title
    form.body.data = article.body
    form.categorys.data=article.category
    form.tags.data = article.tags
    return render_template('admin/article.html',form=form)


@admin.route('/delete/article/<int:article_id>')
@admin_required
def delete_article(article_id):
    article = Article.query.get_or_404(article_id)
    db.session.delete(article)
    db.session.commit()
    flash('Article Deleted','success')
    return redirect_back()


@admin.route('/add/category',methods=['POST','GET'])
@admin_required
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data)
        db.session.add(category)
        db.session.commit()
        flash('Added Category','success')
        return redirect(url_for('admin.add_category'))
    return render_template('admin/category.html',form=form)


@admin.route('/edit/category/<int:category_id>', methods=['POST', 'GET'])
@admin_required
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    form = CategoryForm()
    if form.validate_on_submit():
        category.name = form.name.data
        db.session.commit()
        flash('Category Updated', 'success')
        return redirect(url_for('routes.home'))
    form.name.data = category.name
    return render_template('admin/category.html',form=form)

@admin.route('/delete/category/<int:category_id>')
@admin_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    flash('Category Deleted','success')
    return redirect_back()


@admin.route('/add/tag',methods=['POST','GET'])
@admin_required
def add_tag():
    form = TagsForm()
    if form.validate_on_submit():
        tag = Tag(name=form.name.data)
        db.session.add(tag)
        db.session.commit()
        flash('Added Tag','success')
        return redirect(url_for('admin.add_tag'))
    return render_template('admin/tag.html',form=form)


@admin.route('/edit/tag/<int:tag_id>', methods=['POST', 'GET'])
@admin_required
def edit_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    form = TagsForm()
    if form.validate_on_submit():
        tag.name = form.name.data
        db.session.commit()
        flash('Tag Updated', 'success')
        return redirect(url_for('routes.home'))
    form.name.data = tag.name
    return render_template('admin/tag.html',form=form)

@admin.route('/delete/tag/<int:tag_id>')
@admin_required
def delete_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    flash('Tag Deleted', 'success')
    return redirect_back()

