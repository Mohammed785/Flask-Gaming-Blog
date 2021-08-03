from .models import Notification
from .extensions import db
from flask import url_for



def article_notification(article_id,receiver):
    message = f"New Article Posted Check it now <a href='{url_for('routes.show_article',article_id=article_id)}'></a>"
    notification = Notification(body=message,receiver=receiver)
    db.session.add(notification)
    db.session.commit()

def security_notification(receiver):
    message = f"Security Alert Some one trying to open your account if it was you ignore this mesage"
    notification = Notification(body=message,receiver=receiver)
    db.session.add(notification)
    db.session.commit()

def comment_notification(article_id,receiver):
    message = f"Some one mentioned you in a comment <a href='{url_for('routes.show_article',article_id=article_id)}'></a>"
    notification = Notification(body=message, receiver=receiver)
    db.session.add(notification)
    db.session.commit()
