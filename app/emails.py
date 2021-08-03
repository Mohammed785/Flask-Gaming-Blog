from .extensions import mail
from flask_mail import Message
from threading import Thread
from flask import render_template,current_app

def send_async_mail(app,email):
    with app.app_context():
        mail.send(email)


def send_mail(to,subject,templates,**kwargs):
    message = Message(subject,recipients=[to])
    message.body = render_template(templates+'.txt',**kwargs)
    message.html = render_template(templates+'.html',**kwargs)
    app = current_app.get_current_object()
    thread = Thread(target=send_async_mail,args=[app,message])
    thread.start()
    return thread


def send_reset_token(token,user):
    return send_mail(to=user.email,subject='Reset Password',templates='reset_password',token=token)

def send_news_email(to,**kwargs):
    return send_mail(to=to,subject='New News',templates='new_news',**kwargs)
    
def send_security_email(to,**kwargs):
    return send_mail(to=to,subject='Security Alert',templates='security',**kwargs)
