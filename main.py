from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:indominus@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'ykk3147'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.String(1250))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, content, owner):
        self.title = title
        self.content = content
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password = password

@app.before_request
def require_login():
    need_login = ['newpost', 'logout']
    if request.endpoint in need_login and 'username' not in session:
        if request.endpoint == 'logout':
            flash('You must login before you can logout!', 'error')
        else:
            flash('You must login before you may post!', 'error')
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in!")
            return redirect('/')
        elif user and user.password != password:
            flash('Incorrect password; please double check and try again!', 'error')
        else:
            flash('Username not found; please double check and try again!', 'error')

    return render_template('login.html', title="Login")

@app.route('/signup', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(email=email).first()
        existing_username = User.query.filter_by(username=username).first()

        if existing_user and not existing_username:
            flash('An account already exists for that email, please login!', 'error')
            return redirect('/login')
        elif existing_username and not existing_user:
            flash('That username is already taken, please choose another!', 'error')
            return render_template('signup.html', email=email, title="Sign-up")
        elif len(password) < 3:
            flash('Invalid password; please use a password 3 characters or longer', 'error')
        elif len(username) < 3:
            flash('Invalid username; please use a password 3 characters or longer', 'error')
        elif password != verify:
            flash('Passwords do not match; please check and try again', 'error')
        else:
            new_user = User(email, username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
            
    return render_template('signup.html', title="Sign-up")
        

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if not session['username']:
        return redirect('/login')

    title_error = ''
    content_error = ''
    owner = User.query.filter_by(username=session['username']).first()
    

    if request.method == 'POST':
        title = request.form['title']
        if len(title) == 0:
            title_error = "Please include a title!"
        content = request.form['content']
        if len(content) == 0:
            content_error = "Please write a blog!"
        if len(title) > 0 and len(content) > 0:
            new_blog = Blog(title, content, owner)
            db.session.add(new_blog)
            db.session.commit()

            return redirect('/')
        
    return render_template("newpost.html", title_error=title_error, content_error=content_error, title="New Post")

@app.route('/', methods=['POST', 'GET'])
def index():
        users = User.query.all()
        return render_template("index.html", title="Main Page", users=users)

@app.route('/user')
def user_page():
    user = request.args.get('username')
    owner_id = User.query.filter_by(username=user).first().id
    blogs = Blog.query.filter_by(owner_id=owner_id).all()
    number_posts = 0
    for i in blogs:
        number_posts += 1
    title = str(user) + "'s Blog Posts"
    return render_template('singleUser.html', user=user, title=title, blogs=blogs, number_posts=number_posts)

@app.route('/blog')
def display_blog():
    blog_id = request.args.get('id')
    if not blog_id:
        blog = Blog.query.all()
    else:
        blog = Blog.query.filter_by(id=blog_id)
    return render_template("blog.html", blog=blog)

if __name__ == '__main__':
    app.run()