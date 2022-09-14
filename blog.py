from flask import (Blueprint, flash, g, redirect, render_template, request, url_for)
from werkzeug.exceptions import abort
from Fantasyproject.auth import login_required
from Fantasyproject.db import get_db

bp = Blueprint('blog', __name__, url_prefix='/blog')

#finally bringing in the index for when the Login page was failing b/c it was not being re-directed to index. 
@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts) #using the render_template to pull in the blog/index.html template. 

#route to the /create.html file on blog. 
# This is the start of the Create view. Notice that the create view does not use (return post) different to the update view. 
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

# This is the start of the update view.
# In order to check if the author (user_id) is verified. If not, we will get an error 404 or 403.  
# the update view ends up using the return post function. 
def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

# the update() function takes in an actual id. This is taken from the route function /<int:id>/update. It can also be passed as 1/update. But we are actually specifying the id as int --> <int:id>. the update view uses a post
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None
        if not title: #user has to input a title. 
            error = 'Title is required.'
        if error is not None:
            flash(error)
        else: #if error does not exist, do the following function. 
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index')) #the url_for() function is generating a url for the update page. 
    return render_template('blog/update.html', post=post) #this is redirecting us to the file that is called update.html. 

#Now we are working with the DELETE blog.
#Delete buttons do not have their own template (html) as it is already part of the update.html template. 
#on the update.html file <form action="{{ url_for('blog.delete', id=post['id']) }}" method="post">

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))