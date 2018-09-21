import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Items(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    title = Column(String(64), nullable= False)
    description = Column(String(250), nullable=False)
    category = Column(String(64), nullable=False)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    email = Column(String(64))
    password = Column(String(64))


engine = create_engine(
'sqlite:///item_catalog.db')

Base.metadata.create_all(engine)