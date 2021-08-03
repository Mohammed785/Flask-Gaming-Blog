from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField,FloatField,TextAreaField,SelectMultipleField
from wtforms.validators import ValidationError,DataRequired,Email,EqualTo,Length,Optional,NumberRange
from flask_wtf.file import FileField,FileAllowed
from app.models import Tag,Category
from .models import User
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from flask_login import current_user

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(),Length(min=2,max=30)])
    email = StringField('Email', validators=[DataRequired(),Email()])
    password = PasswordField('Password', validators=[DataRequired(),Length(min=8,max=30)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email Is Already Taken')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),Email()])
    password = PasswordField('Password', validators=[DataRequired(),Length(min=8,max=30)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class AccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=30)])
    email = StringField('Email', validators=[DataRequired(),Email()])
    about = TextAreaField('About',validators=[Optional(),Length(min=2)])
    profile_pic = FileField('Profile Picture',validators=[Optional(),FileAllowed(['jpg','png'])])
    submit = SubmitField('Save')

    def validate_email(self, email):
        if email.data!=current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email Is Already Taken')


class ResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),Email()])
    submit = SubmitField('Find')

    
class ChangePasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=30)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Save')


class CommentForm(FlaskForm):
    body = TextAreaField('Comment',validators=[DataRequired(),Length(min=2)])
    submit = SubmitField('Add')


def category_query():
    return Category.query
def tag_query():
    return Tag.query


class ArticleForm(FlaskForm):
    title = StringField('Title',validators=[DataRequired(),Length(min=10,max=150)])
    body = TextAreaField('Article', validators=[DataRequired(), Length(min=2)])
    pic = FileField('Picture', validators=[DataRequired(), FileAllowed(['jpg', 'png'])])
    review = FloatField('Review' ,validators=[Optional(),NumberRange(0,10)])
    categorys = QuerySelectMultipleField(label='Categorys', query_factory=category_query, allow_blank=True)
    tags = QuerySelectMultipleField(label='Tags', query_factory=tag_query, allow_blank=True)
    submit = SubmitField('Add')

class CategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Add')

class TagsForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Add')


class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)
