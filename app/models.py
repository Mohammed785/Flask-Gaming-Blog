from .extensions import db
from datetime import datetime
from werkzeug.security import check_password_hash,generate_password_hash
from flask_login import UserMixin
from app.search import add_to_index,query_index,remove_from_index


class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    social_id =db.Column(db.String(30))
    username = db.Column(db.String(30))
    email = db.Column(db.String(100),unique=True)
    password = db.Column(db.String(150))
    about = db.Column(db.Text)
    profile_pic = db.Column(db.String(60),default='default.png')
    is_admin = db.Column(db.Boolean, default=False)
    published = db.relationship('Article', backref='author',lazy='dynamic')
    comment = db.relationship('Comment',backref='author',cascade='all',lazy='dynamic')
    notification = db.relationship('Notification',backref='receiver',cascade='all',lazy='dynamic')

    def __repr__(self):
        return f'username:{self.username},email:{self.email}'

    def set_password(self,password):
        self.password = generate_password_hash(password,method='sha256')
    
    def verify_password(self,password):
        return check_password_hash(self.password,password)
    

articles_category = db.Table('Categorys',
                db.Column('article_id',db.Integer,db.ForeignKey('article.id'),primary_key=True),
                db.Column('category_id',db.Integer, db.ForeignKey('category.id'), primary_key=True)
                )
articles_tags = db.Table('Tags',
                db.Column('article_id',db.Integer,db.ForeignKey('article.id'),primary_key=True),
                db.Column('tag_id',db.Integer, db.ForeignKey('tag.id'), primary_key=True)
                )

comments_replies = db.Table('Comments',
                            db.Column('replier_id',db.Integer, db.ForeignKey(
                                'comment.id'), primary_key=True),
                            db.Column('replied_id',db.Integer, db.ForeignKey(
                                'comment.id'), primary_key=True)
                            )


class SearchableMixin(object):
    @classmethod
    def search(cls,expression,page,per_page):
        ids,total = query_index(cls.__tablename__,expression,page,per_page)
        if total==0:
            return cls.query.filter_by(id=0),0
        when = []
        for i in range(len(ids)):
            when.append((ids[i],i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when,value=cls.id),total
        )

    @classmethod
    def before_commit(cls,session):
        session._change = {
            'add':list(session.new),
            'update':list(session.dirty),
            'delete':list(session.deleted)
        }

    @classmethod
    def after_commit(cls,session):
        for obj in session._changes['add']:
            if isinstance(obj,SearchableMixin):
                add_to_index(obj.__tablename__,obj)
        
        for obj in session._changes['update']:
            if isinstance(obj,SearchableMixin):
                add_to_index(obj.__tablename__,obj)

        for obj in session._changes['delete']:
            if isinstance(obj,SearchableMixin):
                remove_from_index(obj.__tablename__,obj)
        
        session._changes = None
    
    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__,obj)


db.event.listen(db.session,'before_commit',SearchableMixin.before_commit)
db.event.listen(db.session,'after_commit',SearchableMixin.after_commit)


class Article(SearchableMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150),nullable=False)
    body = db.Column(db.Text,nullable=False)
    review_score = db.Column(db.Float)
    views_count = db.Column(db.Integer,default=0)
    is_review = db.Column(db.Boolean, default=False)
    article_pic = db.Column(db.String(60),default='default.png')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    tags = db.relationship('Tag',secondary=articles_tags,backref='articles',lazy='dynamic')
    category = db.relationship('Category',secondary=articles_category,backref='articles',lazy='dynamic')
    comments = db.relationship('Comment',backref='article',lazy='dynamic',cascade='all')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __repr__(self):
        return f'title:{self.title},date:{self.timestamp}'
    
    __searchable__ = ['title']


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20),nullable=False,unique=True)

    def __repr__(self):
        return f'{self.name}'

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False,unique=True)

    def __repr__(self):
        return f'{self.name}'

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    replies = db.relationship(
        'Comment',secondary=comments_replies,
        primaryjoin=(comments_replies.c.replier_id==id),
        secondaryjoin = (comments_replies.c.replied_id==id),
        backref= 'opinion',lazy='dynamic'
    )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    article_id = db.Column(db.Integer,db.ForeignKey('article.id'))

    def __repr__(self):
        return f'comment:{self.body} ,date:{self.timestamp}'

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime,default=datetime.utcnow())
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    def __repr__(self):
        return f'body:{self.body} ,date:{self.timestamp}'
