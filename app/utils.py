import os
from secrets import token_hex
from flask import redirect,url_for,request,current_app
from urllib.parse import urljoin,urlparse
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous.exc import BadTimeSignature,BadSignature
from flask_login import current_user
from PIL import Image
from .models import User
from app.notifications import security_notification
def generate_token(user,expire_sec=1800):
    s = Serializer(current_app.config['SECRET_KEY'],expire_sec)
    return  s.dumps({'user_id':user.id}).decode('utf-8')


def verify_token(token):
    s=Serializer(current_app.config['SECRET_KEY'])
    try:
        user_id=s.loads(token)['user_id']
        locals()
    except (BadSignature,BadTimeSignature):
        security_notification(User.query.get(int(user_id)))
        return None
    
    return User.query.get(int(user_id))



def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url,target))
    return test_url.scheme in ('http','https') and ref_url.netloc == test_url.netloc


def redirect_back(default='routes.home',**kwargs):
    for target in request.referrer,request.args.get('next'):
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default,**kwargs))

def change_user_pic(pic):
    _,ext = os.path.splitext(pic.filename)
    new_name = token_hex(10)+ext
    pic_path = os.path.join(current_app.root_path,'static/user',new_name)
    perv_path = os.path.join(current_app.root_path,'static/user',current_user.profile_pic)
    if perv_path and current_user.profile_pic !='default.png':
        os.remove(perv_path)
    size = (400,400)
    i= Image.open(pic)
    i.thumbnail(size)
    i.save(pic_path)
    return new_name

def article_pic(pic):
    _, ext = os.path.splitext(pic.filename)
    new_name = token_hex(10)+ext
    pic_path = os.path.join(current_app.root_path, f'static/article', new_name)
    size = (1500, 1200)
    i = Image.open(pic)
    i.thumbnail(size)
    i.save(pic_path)
    return new_name
