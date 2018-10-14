# Purely for populating first few entries of database

# Importing and connecting to database.
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Items, User
engine = create_engine('sqlite:///item_catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

newItem1 = Items(title = 'Snowboard', description = 'This is used in icey terrains and bla bla bla....', category = 'snowboarding',user_id=1)
newItem2 = Items(title = 'football', description = 'The ball which is used to play the sport.', category = 'soccer',user_id=2)
newItem3 = Items(title = 'Nets', description = 'The ball has to pass through this to make the team gain a point.', category = 'basketball',user_id=3)
newItem4 = Items(title = 'Helmet', description = 'Used to protect the keeper from getting head injury.', category = 'baseball',user_id=3)
newItem5 = Items(title = 'pads', description = 'For protecting various stuff!', category = 'frisbee',user_id=4)
newItem6 = Items(title = 'Bag', description = 'For carrying stuff :_|', category = 'rock_climbing',user_id=5)
newItem7 = Items(title = 'The Table', description = 'Literally the only piece of equipment in foosball.', category = 'foosball', user_id=1)
newItem8 = Items(title = 'stick', description = 'Used to hit the strike.', category = 'hockey',user_id=1)

# To be added and replace the repetitive code 
# for populating databases.
# category_json = json.loads("""{
# "all_categories": [
#   {
#     "title": null,
#     "description": 29,
#     "category": "Books",
#     "user_id": 1
#   },
#   {
#     "created_date": null,
#     "id": 21,
#     "name": "Camping",
#     "no_of_visits": 7
#   },
#   {
#     "created_date": null,
#     "id": 20,
#     "name": "Kitchenware",
#     "no_of_visits": 1
#   },
#   {
#     "created_date": null,
#     "id": 32,
#     "name": "Laptops",
#     "no_of_visits": 10
#   },

#   {
#     "created_date": null,
#     "id": 31,
#     "name": "Susan's Moving Items",
#     "no_of_visits": 8
#   }
# ]
# }""")
# for e in category_json['all_categories']:
# category_input = Category(
#   name=str(e['name']), 
#   id=str(e['id']), 
#   no_of_visits=0, 
#   user_id=1
#   )
session.add(category_input)
session.commit()
session.add(newItem1)
session.add(newItem2)
session.add(newItem3)
session.add(newItem4)
session.add(newItem5)
session.add(newItem6)
session.add(newItem7)
session.add(newItem8)

session.commit()

