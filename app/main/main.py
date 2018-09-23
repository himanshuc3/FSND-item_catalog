from flask import Flask, render_template, request, url_for, flash, redirect, Blueprint, jsonify, session as login_session
#For applying bootstrap integration into flask jinja templates
from flask_bootstrap import Bootstrap

#For login management
from flask_login import LoginManager, login_required, login_user

#For CRUD operations from database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Items, User
from flask_dance.contrib.google import make_google_blueprint, google
import random,string
from form import LoginForm, RegistrationForm, NewItemForm, DeleteForm
import os
from config import data

#Flask instance created
app = Flask(__name__)

# Making the app bootstrap flavoured
bootstrap = Bootstrap(app)

#Congiguration for quering database
engine = create_engine('sqlite:///item_catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
db_session = DBSession()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

# Configuring google oauth blueprint
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' #Configure to accept http oauth request instead of https
google_blueprint = make_google_blueprint(
    client_id = data['google_client_id'],
    client_secret = data['google_client_secret'],
    scope=[
        "https://www.googleapis.com/auth/plus.me",
        "https://www.googleapis.com/auth/userinfo.email"
    ]
)
app.register_blueprint(google_blueprint, url_prefix="/google_login")

auth = Blueprint('auth', __name__)
app.register_blueprint(auth, url_prefix="/auth")

# Default home route
@app.route('/')
def Home():
    if google.authorized:
        return render_template('index.html', logged_in=True)
    return render_template('index.html', logged_in=False)

@app.route('/google')
def google_login():
    if not google.authorized:
        return redirect(url_for('google.login'))
    # return redirect(url_for('Home'))
    return '<h1>Ok. google authorized</h1>'

# Login route
@app.route('/login', methods=['GET','POST'])
def Login():
    # state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    # login_session['state'] = state
    # return 'State is %s' % login_session['state']
    login_form = LoginForm()
    registration_form = RegistrationForm()
    if login_form.validate_on_submit():
        user = db_session.query(User).filter_by(email = login_form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            redirect(url_for('Home'))
        flash('Invalid email or password')
    if registration_form.validate_on_submit():
        user = db_session.query(User).filter_by(email = registration_form.email.data).first()
        if user is None:
            new_user = User(name = registration_form.name.data, email = registration_form.email.data)
            new_user.password = registration_form.password.data
            db_session.add(new_user)
            db_session.commit()
            flash('Registration successful. Please Log in with the credentials')
            redirect(url_for('Login'))
        flash('User already exists. Please log in')
    return render_template('login.html', form=login_form, registration_form = registration_form)

# Show all items when clicked on the catalog
@app.route('/catalog/<string:category_name>/items')
def ItemsByCategory(category_name):
    items_by_category = db_session.query(Items).filter_by(category=category_name).all()
    return render_template('items_by_category.html', category_name=category_name, items=items_by_category)

# Show a specific item
@app.route('/catalog/<string:category_name>/<string:item_name>')
def SpecificItem(category_name, item_name):
    item = db_session.query(Items).filter_by(title=item_name, category=category_name).first()
    print(item.title, item.description)
    return render_template('item_page.html', item = item)

# Adding item route
@app.route('/catalog/new', methods=['GET','POST'])
def NewItem():
    new_item_form = NewItemForm()
    if request.method == 'POST' and new_item_form.validate_on_submit():
        new_item = Items(title = new_item_form.title.data, description = new_item_form.description.data, category = new_item_form.category.data)
        db_session.add(new_item)
        db_session.commit()
        return redirect(url_for('Home'))
    return render_template('new_item.html', new_item_form = new_item_form)

# Editing item
@app.route('/catalog/<string:item_name>/edit')
def EditItem(item_name):
    item_to_edit = db_session.query(Items).filter_by(title=item_name).first()
    if item_to_edit :
        render_template('edit_item.html', item = item_to_edit )
    return redirect(url_for('Home'))

# Deleting item route
@app.route('/catalog/<string:item_name>/delete', methods=['GET','POST'])
def DeleteItem(item_name):
    # Checking if item exists in table
    item_to_delete = db_session.query(Items).filter_by(title=item_name).first()
    form = DeleteForm()
    if item_to_delete :
        if request.method == 'POST' :
            db_session.delete(item_to_delete)
            db_session.commit()
            return redirect(url_for('Home'))
        return render_template('delete_item.html', delete_form = form)
    return redirect(url_for('Home'))

# Route doesn't exist
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404


if __name__ == '__main__':
    app.secret_key = data['secret_key']
    #Enables reloader and debugger
    app.debug = True
    #Starting flask application at localhost:5000
    app.run(host='0.0.0.0', port=5000)