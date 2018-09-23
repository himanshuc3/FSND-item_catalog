from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Items, User
engine = create_engine('sqlite:///item_catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

items = session.query(Items).all()
for item in items:
    print(item.id)
    print(item.title)
    print(item.description)
    print(item.category)
    print("-----")