from flask import Blueprint,redirect,render_template,request,url_for,flash
from flask_login import login_required,login_user,logout_user
from app.decorators import check_login
from app.utils import generate_token,verify_token
from app.forms import LoginForm,RegisterForm,ResetRequestForm,ChangePasswordForm
from app.models import User
from app.extensions import db
from app.oauth import OAuthSignIn
from app.emails import send_reset_token
from app.notifications import security_notification

auth =Blueprint('auth',__name__)


@auth.route('/login',methods=['POST','GET'])
@check_login
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if user.verify_password(form.password.data):
                login_user(user,remember=form.remember.data)
                flash('Logged In Successfully','success')
                next_des = request.args.get('next')
                return redirect(next_des) if next_des else redirect(url_for('routes.home'))
            else:
                flash('Wrong Password','danger')
        else:
            flash('User not found','danger')
    return render_template('auth/login.html',form=form)


@auth.route('/register',methods=['POST','GET'])
@check_login
def register():
    form=RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registed Successfully Now You Can Login','success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html',form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged Out User','success')
    return redirect(url_for('routes.about'))


@auth.route('/authorize/<provider_name>')
def oauth_authorize(provider_name):
    provider = OAuthSignIn.get_provider(provider_name)
    return provider.authorize()


@auth.route('/callback/<provider>')
def oauth_callback(provider):
    oauth =OAuthSignIn.get_provider(provider)
    social_id ,name,email = oauth.callback(provider)
    if social_id is None:
        flash('Authentication Failed','danger')
        return redirect(url_for('auth.login'))
    
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(username=name,email=email,social_id=social_id)
        db.session.add(user)
        db.session.commit()
    login_user(user,True)
    flash('Logged In Successfully','success')
    return redirect(url_for('routes.home'))

@auth.route('/reset/request',methods=['POST','GET'])
def reset_request():
    form = ResetRequestForm()
    if form.validate_on_submit():
        user= User.query.filter_by(email=form.email.data).first()
        if not user:
            flash('User Does Not Exists','danger')
        token = generate_token(user)
        send_reset_token(token,user)
        flash('Email Sent With Instrutions To Reset Password','success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_request.html',form=form)


@auth.route('/reset/password/<token>',methods=['POST','GET'])
def reset_password(token):
    user=verify_token(token)
    if not user:
        flash('Invalid Or Expired Token', 'danger')
        return redirect(url_for('auth.forget_password'))
    form= ChangePasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Password Has Been Changed', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
