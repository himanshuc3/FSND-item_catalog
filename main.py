from flask import Flask, render_template, request, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Items

app = Flask(__name__)

engine = create_engine('sqlite:///item_catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Deafult home route
@app.route('/')
@app.route('/catalog')
def Home():
    return render_template('index.html')

# Show all items when clicked on the catalog
@app.route('/category/<string:category_name>')
def ItemsByCategory(category_name):
    return render_template('items_by_category.html')

# Show a specific item
@app.route('/category/<string:category_name>/item/<int:item_id>')
def ItemById(category_name, item_id):
    return render_template('item_page.html')

# Login route
@app.route('/login')
def Login():
    return render_template('items_by_catalog.html')

# Adding new item route
@app.route('/item/new')
def NewItem():
    return render_template('new_item.html')

# Editing item route
@app.route('/item/edit')
def EditItem():
    return render_template('edit_item.html')

# Deleting item route
@app.route('/item/delete')
def DeleteItem():
    return render_template('delete_item.html')


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
