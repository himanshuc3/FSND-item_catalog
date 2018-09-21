from flask import Flask, render_template, request, url_for, flash, redirect, jsonify, session as login_session
from flask_bootstrap import Bootstrap
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Items, User
from flask_dance.contrib.google import make_google_blueprint, google
import random,string
from form import LoginForm, RegistrationForm
import os
from data import data as data


app = Flask(__name__)

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

# Making the app bootstrap flavoured
bootstrap = Bootstrap(app)

engine = create_engine('sqlite:///item_catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
db_session = DBSession()

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
    # if login_form.validate_on_submit():
    # if registration_form.validate_on_submit():
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

# Adding/Editing item route
@app.route('/catalog/<string:item_name>/edit')
def NewItem(item_name):
    return render_template('edit_item.html')

# Deleting item route
@app.route('/catalog/<string:item_name>/delete')
def DeleteItem(item_name):
    return render_template('delete_item.html')

# Route doesn't exist
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404


if __name__ == '__main__':
    app.secret_key = data['secret_key']
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
