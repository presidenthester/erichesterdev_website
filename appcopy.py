from flask import Flask, render_template, request,redirect, url_for,flash
from webforms import ContactForm, UserForm, PostForm, LoginForm, SearchForm
import smtplib
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import asc, desc
from flask_login import UserMixin, login_user, logout_user ,LoginManager, login_required, current_user
from flask_ckeditor import CKEditor







app = Flask(__name__)
ckeditor = CKEditor(app)
app.config['CKEDITOR_PKG_TYPE'] = 'full'


app.config['SQLALCHEMY_DATABASE_URI'] = 'your own code here'

app.config['SECRET_KEY'] = 'your own secret key here'

UPLOAD_FOLDER = 'static/profile_imgs/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)
app.app_context().push()

migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

with app.app_context():
    db.create_all()  


@app.route('/about')
def about():
    title = ' | About Me'
    return render_template('about.html', title=title)


@app.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():

    form = PostForm()
    
    if form.validate_on_submit():
        poster = current_user.id
        post   = Posts(title   =form.title.data,
                     content   =form.content.data,
                     poster_id =poster,
                     slug      =form.slug.data)
        
        form.title.data   = ''
        form.content.data = ''
        form.author.data  = ''
        form.slug.data    = ''
        
        db.session.add(post)
        db.session.commit()
        
    return render_template('add_post.html', form=form)


@app.route('/add_user', methods=['GET', 'POST'])  
def add_user():
    name = None
    form=UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            hashed_pw = generate_password_hash(form.password_hash.data, 'sha256')
            user = Users(username=form.username.data,
                         name=form.name.data, 
                         email=form.email.data,
                         password_hash=hashed_pw)
            
            db.session.add(user)
            db.session.commit()
            
        name = form.name.data
        
        form.name.data          = ''
        form.username.data      = ''
        form.email.data         = ''
        form.password_hash.data = ''
        
    our_users = Users.query.order_by(Users.date_added)
    return render_template('add_user.html', form=form, 
                                            name=name, 
                                            our_users=our_users)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    
    form     = ContactForm()
    sender   = 'your email address here'
    password = 'your email password here'
    name     = None
    
    
    
    if request.method == 'POST':
        name    = request.form['name']
        email   = request.form['email']
        message = request.form['message']
        
        try:
            smtp_server = smtplib.SMTP('smtp.titan.email', 587)
            smtp_server.starttls()
            smtp_server.login(sender, password)
            
            subject = f'Contact Form Submission from {name}'
            body    = f'Name: {name}\nEmail: {email}\nMessage: {message}'
            msg     = f'Subject: {subject}\n\n{body}'
            
            smtp_server.sendmail(sender, sender, msg)
            smtp_server.quit()
            
        except Exception as e:
            print(f"Email sending failed: {e}")
            
        
    
    return render_template('contact.html', form=form, name=name)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    
    
    if request.method == 'POST':
        name_to_update.name     = form.name.data
        name_to_update.email    = form.email.data
        name_to_update.username = form.username.data
        
        
       
        try:
            db.session.commit()
            
            return render_template('dashboard.html', form=form, name_to_update=name_to_update)
            
        except:
            return render_template('dashboard.html', form=form, name_to_update=name_to_update)
         
    else:
        return render_template('dashboard.html', form=form, name_to_update=name_to_update, id=id)


@app.route('/delete/<int:id>')
def delete(id):
    
    name = None
    form=UserForm()
    user_to_delete = Users.query.get_or_404(id)
    
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        
        our_users = Users.query.order_by(Users.date_added)
        return render_template('add_user.html', form=form, name=name, our_users=our_users)

    except:
        return render_template('add_user.html', form=form, name=name, our_users=our_users)
  
  
@app.route('/portfolio/delete/<int:id>')
@login_required
def delete_post(id):
    
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster.id:
    
        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            
            return redirect(url_for('portfolio'))
        
        except:
            
            return redirect(url_for('portfolio'))
    else:
        return redirect(url_for('portfolio'))
        
  
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
       user = Users.query.filter_by(username=form.username.data).first()
       if user:
           if check_password_hash(user.password_hash, form.password.data):
               login_user(user)
               return redirect(url_for('dashboard'))
           
    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET', 'POST']) 
@login_required 
def logout():
    logout_user() 
    return redirect(url_for('login')) 


@app.route('/portfolio')
def portfolio():
    title = ' | Portfolio - Blog'
    posts = Posts.query.order_by(desc(Posts.date_posted))
    return render_template('portfolio.html', title=title, posts=posts)


@app.route('/portfolio/<int:id>')
def post_page(id):
    post = Posts.query.get_or_404(id)
    return render_template('post_page.html', post=post)
  
    
@app.route('/portfolio/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        
        post.title   = form.title.data
        post.slug    = form.slug.data
        post.content = form.content.data
        
        db.session.add(post)
        db.session.commit()
        
        return redirect(url_for('post_page', id=post.id))
    
    if current_user.id == post.poster.id:
        form.title.data   = post.title
        form.slug.data    = post.slug
        form.content.data = post.content 
        
        return render_template('edit_post.html', form=form, post=post, id=id) 
    
    else:
        return redirect(url_for('post_page', id=post.id))

@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    posts = Posts.query

    if form.validate_on_submit():
        searched_term = form.searched.data
        posts = posts.filter(Posts.content.like('%' + searched_term + '%'))
        posts = posts.order_by(Posts.title).all()
        return render_template("search.html", form=form, searched=searched_term, posts=posts)
    else:
        flash("Search field cannot be empty.")
        return redirect(url_for('index')) 

    

@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    
    if request.method == 'POST':
        name_to_update.name = form.name.data
        name_to_update.email = form.email.data
        name_to_update.username = form.username.data
        
        
        try:
            db.session.commit()
            
            return render_template('update.html', form=form, name_to_update=name_to_update)
        except:
            
            return render_template('update.html', form=form, name_to_update=name_to_update)
    
            
    
    else:
        return render_template('update.html', form=form, name_to_update=name_to_update, id=id)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'),500

class Posts(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(255))
    slug        = db.Column(db.String(255))
    content     = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.now())
    poster_id   = db.Column(db.Integer, db.ForeignKey("users.id"))

class Users(db.Model, UserMixin):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(255), nullable=False, unique=True)
    name          = db.Column(db.String(100), nullable=False)
    email         = db.Column(db.String(150), nullable=False, unique=True)
    date_added    = db.Column(db.DateTime, nullable=False, default=datetime.now())
    password_hash = db.Column(db.String(128))
    
    posts         = db.relationship("Posts", backref='poster')
    
    
    
    
    @property
    def password(self):
        raise AttributeError('Password is not readable!')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    
    def __repr__(self):
        return '<Name %r>' % self.name



  
  
        





        





















    
    






    

if __name__ == '__main__':
    app.run(debug=True)

