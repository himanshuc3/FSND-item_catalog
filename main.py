from flask import Flask, render_template, \
    request, url_for, flash, redirect, Blueprint, \
    session as login_session, make_response, jsonify
# For applying bootstrap integration into flask jinja templates
from flask_bootstrap import Bootstrap

# For login management
from flask_login import LoginManager, login_required, login_user, logout_user
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

# For creating restFUL API
from flask_restful import Resource, Api

# For CRUD operations from database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from database_setup import Base, Items, User
from flask_dance.contrib.google import make_google_blueprint, google
import random
import string
from form import LoginForm, RegistrationForm, NewItemForm, DeleteForm
import os
import json
import httplib2
import requests
from config import config

# Flask instance created
app = Flask(__name__)

# Making the app bootstrap flavoured
bootstrap = Bootstrap(app)

# Initializing api instance
api = Api(app)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

# Congiguration for quering database
# Also make session scoped
engine = create_engine('sqlite:///item_catalog.db')
Base.metadata.bind = engine
db_session = scoped_session(sessionmaker(bind=engine))


# Removes session after every thread aka function view (routes)
@app.teardown_request
def remove_session(ex=None):
    db_session.remove()


login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return db_session.query(User).get(int(user_id))


# Configuring google oauth blueprint
# os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
# #Configure to accept http oauth request instead of https
# google_blueprint = make_google_blueprint(
#     client_id = data['google_client_id'],
#     client_secret = data['google_client_secret'],
#     scope=[
#         "https://www.googleapis.com/auth/plus.me",
#         "https://www.googleapis.com/auth/userinfo.email"
#     ]
# )
# app.register_blueprint(google_blueprint, url_prefix="/google_login")


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'])
    db_session.add(newUser)
    db_session.commit()
    user = db_session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = db_session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = db_session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Default home route
@app.route('/', methods=['GET'])
def Home():
    latest_items = db_session.query(Items).order_by(Items.id.desc()).limit(5)
    return render_template(
                        'index.html',
                        latest_items=latest_items,
                        login_session=login_session
                        )


# Login route
@app.route('/login', methods=['GET', 'POST'])
def Login():
    login_form = LoginForm()
    if login_form.submit1.data and login_form.validate_on_submit():
        user = (
            db_session
            .query(User)
            .filter_by(email=login_form.email.data)
            .first()
        )
        if user is not None and user.verify_password(login_form.password.data):
            login_user(user, login_form.remember_me.data)
            login_form.email.data = ''
            login_form.password.data = ''
            return redirect(url_for('Home'))
        flash('Invalid email or password')
    return render_template(
                        'login.html',
                        form=login_form,
                        login_session=login_session
                        )


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
                    json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    return redirect(url_for('Home'))


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(
                    json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is %s', access_token)
    print('User name is: ')
    print(login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % \
            login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        return redirect(url_for('Home'))
    else:
        response = make_response(
                    json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/register', methods=['GET', 'POST'])
def Register():
    registration_form = RegistrationForm()
    if registration_form.submit2.data and \
        registration_form.validate_on_submit():
        user = (
            db_session
            .query(User)
            .filter_by(email=registration_form.email.data)
            .first()
        )
        if user is None:
            new_user = User(
                        name=registration_form.name.data,
                        email=registration_form.email.data
                        )
            new_user.password = registration_form.password.data
            db_session.add(new_user)
            db_session.commit()
            flash('Registration successful. \
                Please Log in with the credentials')
            return redirect(url_for('Home'))
        flash('User already exists. Please log in')
    return render_template('register.html', form=registration_form)


@app.route('/google_login')
def GoogleLogin():
    # Create anti-forgery state token
    state = ''.join(
            random.choice(string.ascii_uppercase + string.digits)
            for x in range(32))
    login_session['state'] = state
    return render_template('google_login.html', STATE=state)

# Logging out
# @app.route('/logout')
# @login_required
# def Logout():
#     logout_user()
#     flash('You have been logged out')
#     return redirect(url_for('Home'))


# Show all items when clicked on the catalog
@app.route('/catalog/<string:category_name>/items')
def ItemsByCategory(category_name):
    items_by_category = (
                        db_session
                        .query(Items)
                        .filter_by(category=category_name)
                        .all()
    )
    return render_template(
                    'items_by_category.html',
                    category_name=category_name,
                    items=items_by_category,
                    login_session=login_session
                    )


# Show a specific item
@app.route('/catalog/<string:category_name>/<string:item_name>')
def SpecificItem(category_name, item_name):
    item = (
        db_session
        .query(Items)
        .filter_by(title=item_name, category=category_name)
        .first()
    )
    print(item.title, item.description)
    return render_template(
            'item_page.html',
            item=item,
            login_session=login_session
            )


# Adding item route
@app.route('/catalog/new', methods=['GET', 'POST'])
def NewItem():
    if 'username' not in login_session:
        return redirect(url_for('Home'))
    new_item_form = NewItemForm()
    if request.method == 'POST' and \
        new_item_form.validate_on_submit() and \
        'username' in login_session:
        new_item = Items(
                    title=new_item_form.title.data,
                    description=new_item_form.description.data,
                    category=new_item_form.category.data,
                    user_id=login_session['user_id']
                    )
        db_session.add(new_item)
        db_session.commit()
        return redirect(url_for('Home'))
    return render_template(
            'new_item.html',
            new_item_form=new_item_form,
            login_session=login_session
            )


# Editing item
@app.route(
    '/catalog/<string:category_name>/<string:item_name>/edit',
    methods=['GET', 'POST']
    )
# @login_required
def EditItem(category_name, item_name):
    if 'username' not in login_session:
        redirect(url_for('Home'))
    item_to_edit = (
                db_session
                .query(Items)
                .filter_by(title=item_name, category=category_name)
                .first()
    )
    if item_to_edit:
        if request.method == 'POST' and \
            'username' in login_session and \
            item_to_edit.user_id == login_session['user_id']:
            title = request.form.get('title')
            description = request.form.get('description')
            category = request.form.get('category')
            item_to_edit.title = title
            item_to_edit.description = description
            category = str(category)
            db_session.add(item_to_edit)
            db_session.commit()
            return redirect(url_for('Home'))
        return render_template(
                'edit_item.html',
                item=item_to_edit,
                login_session=login_session
                )
    return redirect(url_for('Home'))


# Deleting item route
# @login_required
@app.route(
    '/catalog/<string:category_name>/<string:item_name>/delete',
    methods=['GET', 'POST']
    )
def DeleteItem(category_name, item_name):
    if 'username' not in login_session:
        return redirect(url_for('Home'))
    # Checking if item exists in table
    item_to_delete = (
                    db_session
                    .query(Items)
                    .filter_by(title=item_name, category=category_name)
                    .first()
    )
    form = DeleteForm()
    if item_to_delete and \
        'username' in login_session and \
        item_to_delete.user_id == login_session['user_id']:
        if request.method == 'POST':
            db_session.delete(item_to_delete)
            db_session.commit()
            return redirect(url_for('Home'))
        return render_template(
                'delete_item.html',
                delete_form=form,
                login_session=login_session
                )
    return redirect(url_for('Home'))


class Item(Resource):

    def get(self):
        count = db_session.query(Items).count()
        items = db_session.query(Items).all()
        arbitrary_item = items[random.randint(0, count-1)]
        return json.dumps({
                         'id': arbitrary_item.id,
                         'title': arbitrary_item.title,
                         'description': arbitrary_item.description,
                         'category': arbitrary_item.category
                         })


api.add_resource(Item, '/v1/random_catalog/json')


@app.route('/v1/catalog/json')
def allItemsJSON():
    items = db_session.query(Items).all()
    item_dict = [
        {
            'id': i.id,
            'title': i.title,
            'description': i.description,
            'category': i.category
        } for i in items]
    return jsonify(items=item_dict)


# Route doesn't exist
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.secret_key = config['secret_key']
    # Enables reloader and debugger
    app.debug = True
    # Starting flask application at localhost:5000
    app.run(host='0.0.0.0', port=4000)
