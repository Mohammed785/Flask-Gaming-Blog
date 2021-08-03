from app.forms import CommentForm
from flask import Blueprint,render_template,redirect,url_for,flash,request,abort,g
from app.extensions import db
from app.models import Category,Comment,Article,Tag,Notification
from app.utils import redirect_back,change_user_pic
from flask_login import current_user,login_required
from app.forms import AccountForm,SearchForm
from app.notifications import comment_notification

routes = Blueprint('routes',__name__)

@routes.before_app_request
def before_request():
    g.search_form = SearchForm()


@routes.route('/')
def home():
    review_category = Category.query.filter_by(name='Reviews').first()
    platform_category = Category.query.filter_by(name='Platform').first()
    hardware_category = Category.query.filter_by(name='Hardware').first()
    dissection_category = Category.query.filter_by(name='Dissection').first()
    tech_category = Category.query.filter_by(name='Tech').first()
    page = request.args.get('page',1,type=int)
    latest = Article.query.order_by(Article.timestamp.desc()).paginate(page=page,per_page=15)
    reviews = Article.query.with_parent(review_category).paginate(page,per_page=4)
    hardware = Article.query.with_parent(hardware_category).paginate(page,per_page=4)
    dissection = Article.query.with_parent(dissection_category).paginate(page,per_page=5)
    platform = Article.query.with_parent(platform_category).paginate(page,per_page=4)
    tech = Article.query.with_parent(tech_category).paginate(page, per_page=5)
    tags = Tag.query.paginate(page,per_page=10)
    return render_template('routes/home.html',latest=latest,reviews=reviews,hardware=hardware,dissection=dissection,
    platform=platform,tech=tech,tags=tags)


@routes.route('/about')
def about():
    return render_template('routes/about.html')


@routes.route('/account',methods=['POST','GET'])
@login_required
def account():
    form = AccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        if current_user.is_admin:
            current_user.about = form.about.data
        if form.profile_pic.data:
            current_user.profile_pic = change_user_pic(form.profile_pic.data)
        db.session.commit()
        flash('Your Info Has Been Updated','success')
        return redirect(url_for('routes.account'))
    else:
        form.username.data = current_user.username
        form.email.data = current_user.email
        if current_user.is_admin:
            form.about.data = current_user.about
    return render_template('routes/account.html', form=form)


@routes.route('/show/articles')
def show_articles():
    page =request.args.get('page',1,type=int)
    articles = Article.query.order_by(Article.timestamp.desc()).paginate(page,per_page=10)
    return render_template('routes/show_articles.html',articles=articles)


@routes.route('/show/category/<int:category_id>')
def show_category(category_id):
    page = request.args.get('page', 1, type=int)
    category = Category.query.get_or_404(category_id)
    articles = Article.query.with_parent(category).order_by(Article.timestamp.desc()).paginate(page, per_page=8)
    return render_template('routes/show_articles.html', articles=articles, selector=category,type='category')


@routes.route('/show/tag/<int:tag_id>')
def show_tag(tag_id):
    page = request.args.get('page', 1, type=int)
    tag = Tag.query.get_or_404(tag_id)
    articles = Article.query.with_parent(tag).order_by(Article.timestamp.desc()).paginate(page, per_page=8)
    return render_template('routes/show_articles.html', articles=articles, selector=tag, type='tag')


@routes.route('/show/review/all')
def show_reviews():
    page = request.args.get('page', 1, type=int)
    articles = Article.query.filter_by(is_review=True).order_by(Article.timestamp.desc()).paginate(page, per_page=8)
    return render_template('routes/show_articles.html', articles=articles,type='reviews')


@routes.route('/show/article/<int:article_id>',methods=['POST','GET'])
def show_article(article_id):
    article = Article.query.get_or_404(article_id)
    article.views_count+=1
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,author=current_user,article=article)
        db.session.add(comment)
        db.session.commit()
        flash('Comment Added','success')
        return redirect(url_for('routes.show_article',article_id=article_id))
    return render_template('routes/show_article.html', article=article,form=form)


@routes.route('/comment/reply/<int:comment_id>',methods=['POST','GET'])
@login_required
def reply_comment(comment_id):
    comment =Comment.query.get_or_404(comment_id)
    form = CommentForm()
    if form.validate_on_submit():
        reply_comment = Comment(body=form.body.data,author=current_user)
        db.session.add(reply_comment)
        comment.replies.append(reply_comment)
        notification = comment_notification(article_id=comment.article.id, receiver=comment.author)
        db.session.add(notification)
        db.session.commit()
        flash('Replay Added','success')
        return redirect_back()
    return render_template('routes/comment.html',form=form,comment=comment)


@routes.route('/comment/edit/<int:comment_id>',methods=['POST','GET'])
@login_required
def edit_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if current_user != comment.author:
        abort(403)
    form = CommentForm()
    if form.validate_on_submit():
        comment.body =form.body.data
        db.session.commit()
        flash('Comment Updated','success')
        return redirect_back()
    form.body.data = comment.body
    return render_template('routes/comment.html',form=form,comment=comment)


@routes.route('/comment/delete/<int:comment_id>')
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if current_user != comment.author:
        abort(403)
    db.session.delete(comment)
    db.session.commit()
    flash('comment deleted','success')
    return redirect_back()


@routes.route('/notifications')
@login_required
def show_notifications():
    filter = request.args.get('filter')
    if filter=='all':
        notifications = Notification.query.all()
    elif filter=='unread':
        notifications = Notification.query.filter_by(is_read=False).all()
    return render_template('routes/notifications.html', notifications=notifications)

@routes.route('/read/notification/<int:notification_id>')
@login_required
def read_notification(notification_id):
    notification=Notification.query.get_or_404(notification_id)
    notification.is_read = True
    db.session.commit()
    flash('notifications archived.', 'success')
    return redirect(url_for('routes.show_notifications'))

@routes.route('/read/notification/all')
@login_required
def read_all_notification():
    for notification in current_user.notification:
        notification.is_read = True
    db.session.commit()
    flash('All notifications archived.', 'success')
    return redirect(url_for('routes.show_notifications'))


@routes.route('/search')
def search():
    if not g.search_form.validate():
        return redirect_back()
    
    page = request.args.get('page',1,type=int)
    articles,total = Article.search(g.search_form.q.data,page,10)
    next_url = url_for('routes.search',q=g.search_form.q.data,page=page+1) if total> page*10 else None
    prev_url = url_for('routes.search', q=g.search_form.q.data,page=page-1) if page>1 else None

    return render_template('search.html',articles=articles,next_url=next_url,prev_url=prev_url)
    
