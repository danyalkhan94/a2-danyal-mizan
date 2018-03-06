#assignment 2
#PROG38263
#Danyal Khan 991 389 587
#Mizanur Rahman 981388924

from __future__ import division
from datetime import datetime
from collections import Counter

from flask import Flask, session, g, render_template, redirect, url_for, request, flash, abort

from flask_cache import Cache
from flask_mail import Message, Mail
from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from sqlalchemy import desc
from itsdangerous import URLSafeTimedSerializer

# local imports 
from forms import RegistrationForm, LoginForm, ResetPasswordForm, EmailForm


# create the app
app = Flask(__name__)
app.config.from_object('config')

cache  = Cache(app, config={'CACHE_TYPE': 'simple'})
mail   = Mail(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

db = SQLAlchemy(app)



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id        = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    email     = db.Column(db.Text, unique=True, nullable=False)
    firstname = db.Column(db.String(255), nullable=False)
    lastname  = db.Column(db.String(255), nullable=False)
    password  = db.Column(db.String(255))

    occupation = db.Column(db.String(255))
    bio        = db.Column(db.Text)
    logo       = db.Column(db.String, default=app.config['DEFAULT_USER_LOGO'])
    reset      = db.Column(db.Boolean, default=False)
    confirmed  = db.Column(db.Boolean, default=False)
    active     = db.Column(db.Boolean, default=True)
    created    = db.Column(db.DateTime, default=datetime.now())    
      
    def __init__(self, first, last, email, password):
        self.firstname = first
        self.lastname = last
        self.email = email
        self.password = bcrypt.generate_password_hash(password)
        
    def password_correct(self, plaintext):
        return bcrypt.check_password_hash(self.password, plaintext)

    def __repr__(self):
        return '<id {}>'.format(self.id)


class Post(db.Model):
    __tablename__ = 'posts'
    
    id        = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid    = db.Column(db.Integer, db.ForeignKey('users.id'))
    user      = db.relationship('User', backref=db.backref('posts', lazy='dynamic'))
    
    category  = db.Column(db.String(255), nullable=False)
    title     = db.Column(db.String(255), nullable=False)
    text      = db.Column(db.Text, nullable=False)
    link      = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text, default=app.config['DEFAULT_POST_IMG'])
    
    likes     = db.Column(db.Integer, default=0)
    views     = db.Column(db.Integer, default=0)
    
    published = db.Column(db.Boolean, default=True)
    modified  = db.Column(db.DateTime, default=datetime.now()) 
    
    def __init__(self, title, text, category):
        self.title = title
        self.text = text
        self.category = category
        self.link = gen_link(title, datetime.now(), app.config['MAX_LINK_LEN'])
        
    def __repr__(self):
        return '<id {}>'.format(self.id)     


@login_manager.user_loader
def load_user(userid):
    return User.query.filter(User.id==userid).first()
    
    
    
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 


def gen_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=app.config['CONFIRM_EMAIL_TOKEN_EXPIRATION']):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt=app.config['SECURITY_PASSWORD_SALT'], max_age=expiration)
        return email
    except Exception:
        return ''      # empty string doesn't match any email


def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    mail.send(msg)
    
    
def send_confirm_email(email):
    token = gen_confirmation_token(email)
    confirm_url = url_for('confirm_email', token=token, _external=True)
    html = render_template('activate_account.html', confirm_url=confirm_url)
    subject = "Please confirm your email"
    send_email(email, subject, html) 
    
    
def send_reset_password(email):
    token = gen_confirmation_token(email)
    reset_url = url_for('password_reset', token=token, _external=True)
    html = render_template('reset_password.html', email=email, reset_url=reset_url)
    subject = "Reset your password"
    send_email(email, subject, html)


def gen_link(string, date, maxlen):
    '''
    creates an url identifier from given string and date object
    '''
    p = date.strftime("%s")
    t = '-'.join(string.split())
    u = ''.join([c for c in t if c.isalnum() or c == '-'])   # remove punctation   
    strlen = maxlen - len(p) - 1
    return u[:strlen].rstrip('-').lower() + '-' + p 


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 


@cache.cached(timeout=app.config['CACHE_TIMEOUT'], key_prefix='get_categories')
def get_categories():
    return db.session.query(Post.category).filter(Post.published).distinct().order_by(Post.category).all()


@cache.cached(timeout=app.config['CACHE_TIMEOUT'], key_prefix='get_top_stories')
def get_top_stories():
    return Post.query.filter(Post.published).order_by(desc( Post.likes + Post.views/10 )).limit(6).all()
    

@cache.cached(timeout=app.config['CACHE_TIMEOUT'], key_prefix='get_recent_stories')
def get_recent_stories():
    return Post.query.filter(Post.published).order_by(desc( Post.modified )).limit(6).all()
    


@app.before_request
def before_request():
    g._categories  = get_categories()
    g._top_stories = get_top_stories()
    g._recent_stories = get_recent_stories()
        

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 


@app.route('/')
@app.route('/<int(min=1):page>')
@app.route('/category/<category>')
@app.route('/category/<category>/<int(min=1):page>')
def homepage(category=None, page=1):

    posts = Post.query.filter(Post.published)
    if category is not None:    # this category only
        posts = posts.filter(Post.category==category)
    
    posts = posts.order_by(desc( Post.modified )).paginate(page=page, per_page=app.config['PER_PAGE'])
    
    return render_template('homepage.html', posts=posts, category=category)
    
    
@app.route('/posts/<link>')
def view_post(link):
    post = Post.query.filter(Post.published and Post.link==link).first_or_404()
    
    return render_template('view_post.html', post=post)

@app.route('/edit/<link>')
@login_required
def edit_post(link):
    post = Post.query.filter(Post.published and Post.link==link).first_or_404()
    return render_template('edit_post.html', post=post)
    
@app.route('/create', methods=['GET','POST'])
@login_required
def create_post():
    if request.method == 'GET':
        return render_template('edit_post.html', post={})
    elif request.form['publish'] == 'Discard':
        return redirect(url_for('dashboard'))
    else:
        post = Post(request.form['title'], request.form['text'], request.form['category'])
        post.userid = current_user.id
        post.image_url = request.form['image_url']
        post.modified  = datetime.now()
        db.session.add(post)
        db.session.commit()    
        return redirect(url_for('dashboard'))
        

@app.route('/update/<link>', methods=['GET','POST'])
@login_required
def update_post(link):
    if request.method == 'POST':
        if request.form['publish'] == 'Discard':
            return redirect(url_for('dashboard'))
        
        post = Post.query.filter(Post.published and Post.link==link).first_or_404()
        views = post.views
        likes = post.likes
        db.session.delete(post)
        
        post = Post(request.form['title'], request.form['text'], request.form['category'])
        post.userid = current_user.id
        post.image_url = request.form['image_url']
        post.modified  = datetime.now()
        post.views = views
        post.likes = likes
        db.session.add(post)
        db.session.commit()    
        
        return redirect(url_for('dashboard'))
    return abort(404)    


@app.route('/delete/<link>', methods=['GET','POST'])
@login_required
def delete_post(link):
    if request.method == 'POST':
        post = Post.query.filter(Post.published and Post.link==link).first_or_404()
        db.session.delete(post)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return abort(404)        
    
@app.route('/dashboard')
@login_required
def dashboard():
    print(current_user.id, current_user.lastname)
    posts = Post.query.filter(Post.published and Post.userid==current_user.id).order_by(desc( Post.modified ))
    return render_template('dashboard.html', posts=posts)    
    
    
@app.route('/login', methods=['GET', 'POST'])
def login():

    kwargs = {'page_title': 'Login', 'form_title': 'Login', 
              'action': url_for('login'), 
              'primary_button': 'Submit', 
              'links': [("Don't have an account?", url_for('signup')), 
                        ('Forgot your password?', url_for('forgot_password')), 
                        ('Need help?', '#')]
              }
                        
    form = LoginForm(request.form)
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user or not user.password_correct(form.password.data):
            flash('Invalid username or password.', 'danger')
        elif not user.confirmed:  # valid credentials but still needs to confim an account
            token_url = url_for('resend_confirmation', _external=True)
            link = ' <a href="' + token_url + '">Resend confimation link</a>'
            flash('Your account is not confirmed yet.' + link, 'warning')
        else:
            login_user(user)
            return redirect(url_for('dashboard'))
        
    return render_template('formbuilder.html', form=form, **kwargs)    


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('homepage'))    

    
@app.route('/signup', methods=['GET', 'POST'])
def signup():

    kwargs = {'page_title': 'Sign Up', 'form_title': 'Sign Up', 
              'action': url_for('signup'), 
              'primary_button': 'Register', 
              'links': [('Already have an account?', url_for('login')), ('Need help?', '#')]
              }
                        
    form = RegistrationForm(request.form)
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash('Email address is already registered.', 'danger')    # already exists
        else:
            user = User(form.firstname.data, form.lastname.data, form.email.data, form.password.data)
            db.session.add(user)
            db.session.commit()
            
            send_confirm_email(user.email)
            flash('Sign up successful! Check your email for a link to verify your account.', 'success')
            
            return redirect(url_for('homepage'))

    return render_template('formbuilder.html', form=form, **kwargs)
    
    
@app.route('/resend_confirmation', methods=['GET','POST'])
def resend_confirmation():

    kwargs = {'page_title': 'Resend Confirmation', 'form_title': 'Resend Confirmation Token', 
              'action': url_for('resend_confirmation'), 
              'primary_button': 'Submit', 
              'links': [("Don't have an account?", url_for('signup')), ('Need help?', '#')]
              }

    form = EmailForm(request.form)
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash('Cannot find that email, sorry.', 'danger')
        elif user.confirmed:
            flash('Your account has already been verified. You can log in using your credentials', 'info')
        else:
            send_confirm_email(user.email)
            flash('Check your email for a link to verify your account.', 'success')
            
            return redirect(url_for('homepage')) 

    return render_template('formbuilder.html', form=form, **kwargs)           


@app.route('/confirm/<token>')
def confirm_email(token):
    
    email = confirm_token(token)
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('The confirmation link is invalid or has expired.', 'danger')
    elif user.confirmed:
        flash('Your account has already been verified. You can log in using your credentials', 'info')
    else:   # success
        user.confirmed = True 
        db.session.commit()
        
        login_user(user)
        
        flash('You have confirmed your account. Thanks!', 'success')
        return redirect(url_for('dashboard'))
        
    return redirect(url_for('homepage'))


@app.route('/forgot_password', methods=['GET','POST'])
def forgot_password():

    kwargs = {'page_title': 'Reset Password', 'form_title': 'Reset Your Password', 
              'action': url_for('forgot_password'), 
              'primary_button': 'Submit', 
              'links': [("Don't have an account?", url_for('signup')), ('Need help?', '#')]
              }

    form = EmailForm(request.form)
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash('Cannot find that email, sorry.', 'danger')
        else:
            user.reset = True
            db.session.commit()
            
            send_reset_password(user.email)
            flash('Check your email for a link to reset your password.', 'success')
            
            return redirect(url_for('homepage')) 

    return render_template('formbuilder.html', form=form, **kwargs)  


@app.route('/password_reset/<token>', methods=['GET','POST'])
def password_reset(token):

    email = confirm_token(token)
    user = User.query.filter_by(email=email).first()
    
    if user and user.reset:
    
        form = ResetPasswordForm(request.form)
        
        kwargs = {'page_title': 'Reset Password', 'form_title': 'Reset Your Password', 
                  'action': url_for('password_reset', token=token), 
                  'primary_button': 'Submit', 
                  'links': [('Need help?', '#')]
                  }
    
        if form.validate_on_submit():
        
            user.password = bcrypt.generate_password_hash(form.password.data)
            user.reset = False
            db.session.commit()
            
            flash('Your password has been successfully reset. You can log in now.', 'success')
            return redirect(url_for('homepage'))
        
        return render_template('formbuilder.html', form=form, **kwargs)
        
    else:
        flash('The reset password link is invalid or has expired.', 'danger')
        return redirect(url_for('homepage'))

    
    
if __name__ == '__main__':
    app.run(debug=True)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
