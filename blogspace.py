

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