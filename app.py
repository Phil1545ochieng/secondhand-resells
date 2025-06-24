from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import logging

# Enable logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'

basedir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///fallback.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Configure Cloudinary
cloudinary.config()

ADMIN_USERNAME = "Androsvela"
ADMIN_PASSWORD = "Androsvela@23"

# -------------------- Model --------------------
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    category = db.Column(db.String(50))
    buying_price = db.Column(db.String(20))
    selling_price = db.Column(db.String(20))
    reason = db.Column(db.Text)
    location = db.Column(db.String(100))
    contact = db.Column(db.String(100))
    image_filename = db.Column(db.String(300))  # Cloudinary URL
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# -------------------- Helpers --------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# -------------------- Routes --------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/listings')
def listings():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    categories = ["Furniture", "Electronics", "Lands", "Business", "Home Appliance", "Spare Parts"]
    grouped_posts = {cat: [] for cat in categories}
    for post in posts:
        cat = post.category.strip().title()
        grouped_posts.setdefault(cat, []).append(post)
    return render_template('listings.html', grouped_posts=grouped_posts)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Login successful.', 'success')
            return redirect(url_for('post'))
        else:
            flash('Invalid credentials.', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/auto_logout', methods=['POST'])
def auto_logout():
    session.pop('admin_logged_in', None)
    return '', 204

@app.route('/post', methods=['GET', 'POST'])
def post():
    if not session.get('admin_logged_in'):
        flash('Access denied. Please log in as admin.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        buying_price = request.form.get('buying_price')
        selling_price = request.form.get('selling_price')
        reason = request.form.get('reason')
        location = request.form.get('location')
        contact = request.form.get('contact')
        file = request.files.get('image')

        image_filename = None
        if file and allowed_file(file.filename):
            upload_result = cloudinary.uploader.upload(file)
            image_filename = upload_result.get('secure_url')

        new_post = Post(
            title=title,
            category=category,
            buying_price=buying_price,
            selling_price=selling_price,
            reason=reason,
            location=location,
            contact=contact,
            image_filename=image_filename
        )

        db.session.add(new_post)
        db.session.commit()

        flash('Item submitted and saved successfully.', 'success')
        return redirect(url_for('post'))

    return render_template('post.html')

@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if not session.get('admin_logged_in'):
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully.', 'success')
    return redirect(url_for('listings'))

# -------------------- DB Init --------------------
with app.app_context():
    db.create_all()

# -------------------- Run Server --------------------
if __name__ == '__main__':
    app.run(debug=True)
