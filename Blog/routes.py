from flaskBlog import app
from flask import render_template
from flaskBlog.forms import RegistrationForm,LoginForm,PostForm
from flask import flash,request,abort
from flask import url_for,redirect
from flaskBlog.models import User, Post
from flaskBlog import bcrypt,db
from flask_login import login_user, logout_user, current_user, login_required


@app.route('/')
def home():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('index.html',posts=posts)

@app.route('/about')
def about():
    return render_template('about.html',title='About')

@app.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,email=form.email.data,
                    password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account Created for {user.username}','success')
        return redirect(url_for('login'))
    return render_template('register.html',title='Register',form=form)


@app.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user)
            flash(f'You are logged in','success')
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('home'))
        else:
            flash(f'Invalid credentials','danger')
    return render_template('login.html',title='Sign In',form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/create_post',methods=['GET','POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title = form.title.data,description=form.description.data,
                    user_id = current_user.id
                    )
        db.session.add(post)
        db.session.commit()
        flash(f'Post has been created','success')
        return redirect(url_for('home'))
    return render_template('create_post.html',title="Add Post",form=form,heading = "Create Post")

@app.route('/post/<int:post_id>',methods =['GET','POST'])
def get_post(post_id):
    post = Post.query.get(post_id)
    return render_template('get_post.html',filter = f'Post {post_id}',post = post)

@app.route('/post/<int:post_id>/update',methods =['GET','POST'])
def update_post(post_id):
    form = PostForm()
    post = Post.query.get(post_id)
    if current_user != post.author:
        abort(403)

    if form.validate_on_submit():
        post.title = form.title.data
        post.description = form.description.data
        db.session.commit()
        flash('Your post has been updated','success')
        return redirect(url_for('home'))
    elif request.method == 'GET':
        form.title.data = post.title
        form.description.data = post.description
    return render_template('create_post.html',title=f'Update Post {post_id}',form=form,heading = "Update Post")

@app.route('/post/<int:post_id>/delete')
def delete_post(post_id):
    post = Post.query.get(post_id)
    if current_user!=post.author:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('home'))