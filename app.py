from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, Property, User
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///realestate.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'super_secret_key'
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'image')

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()
    if User.query.count() == 0:
        # Create default admin user
        admin_user = User(username='admin', email='admin@example.com', password=generate_password_hash('admin123'), is_admin=True)
        db.session.add(admin_user)
        db.session.commit()
    if Property.query.count() == 0:
        properties = [
            Property(title="Modern Sunset Villa", price="$550,000", location="Beverly Hills, CA", beds=4, baths=3, sqft=2400, image_url="am.jpg", description="This beautiful villa offers a perfect blend of modern architecture and comfortable living.", prop_type="Sale", category="Villa"),
            Property(title="Luxury Skyline Flat", price="$3,500/mo", location="Manhattan, NY", beds=2, baths=2, sqft=1100, image_url="pr.png", description="Luxury Skyline Flat with amazing city views.", prop_type="Rent", category="Apartment"),
            Property(title="Cozy Downtown Studio", price="$2,100/mo", location="Manhattan, NY", beds=1, baths=1, sqft=600, image_url="images.jpg", description="Perfect for young professionals, right in the city center.", prop_type="Rent", category="Studio")
        ]
        db.session.bulk_save_objects(properties)
        db.session.commit()

@app.route('/')
def index():
    location = request.args.get('location')
    prop_type_filter = request.args.get('type')
    max_price = request.args.get('max_price')

    query = Property.query

    if location:
        query = query.filter(Property.location.contains(location))
    if prop_type_filter and prop_type_filter != 'Property Type':
        query = query.filter(Property.category == prop_type_filter)
    if max_price:
        try:
            numeric_max = int(''.join(filter(str.isdigit, max_price)))
            # A bit tricky since price is stored as string "$550,000" or "$3,500/mo" in the DB.
            # For a real app, price should be stored as an Integer column.
            # As a workaround for this demo, we'll fetch all and filter in python.
            all_props = query.all()
            filtered_props = []
            for p in all_props:
                p_val = int(''.join(filter(str.isdigit, p.price.split('/')[0])))
                if p_val <= numeric_max:
                    filtered_props.append(p)
            return render_template('index.html', properties=filtered_props)
        except ValueError:
            pass

    properties = query.all()
    return render_template('index.html', properties=properties)

@app.route('/property/<int:id>')
def property_details(id):
    prop = Property.query.get_or_404(id)
    return render_template('details.html', property=prop)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('admin') if user.is_admin else url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
        elif User.query.filter_by(email=email).first():
            flash('Email already exists.', 'danger')
        else:
            new_user = User(username=username, email=email, password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    properties = Property.query.all()
    return render_template('admin.html', properties=properties)

@app.route('/admin/add', methods=['GET', 'POST'])
@login_required
def add_property():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        image_url = 'am.jpg'
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_url = filename

        new_prop = Property(
            title=request.form.get('title'),
            price=request.form.get('price'),
            location=request.form.get('location'),
            beds=int(request.form.get('beds')),
            baths=int(request.form.get('baths')),
            sqft=int(request.form.get('sqft')),
            image_url=image_url,
            description=request.form.get('description'),
            prop_type=request.form.get('prop_type'),
            category=request.form.get('category')
        )
        db.session.add(new_prop)
        db.session.commit()
        flash('Property added successfully.', 'success')
        return redirect(url_for('admin'))
    return render_template('add_property.html')

@app.route('/admin/delete/<int:id>')
@login_required
def delete_property(id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    prop = Property.query.get_or_404(id)
    db.session.delete(prop)
    db.session.commit()
    flash('Property deleted.', 'success')
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
