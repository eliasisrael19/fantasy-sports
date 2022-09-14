from flask import (Blueprint, flash, g, redirect, render_template, request, url_for)
from werkzeug.exceptions import abort
from Fantasyproject.auth import login_required
from Fantasyproject.db import get_db

bp = Blueprint('stripe', __name__, url_prefix='/stripe')

#finally bringing in the index for when the Login page was failing b/c it was not being re-directed to index. 
@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM stripe_post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('stripe/index.html', posts=posts) #using the render_template to pull in the stripe/index.html template. Passing over to the front-end via this function. #remember that stripe.py should be the "middle" between back and front-end.

