import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Items(Base):
    __tablename__ = 'items'

    id= Column(Integer, primary_key=True)
    title = Column(String(250), nullable= False)
    description = Column(String(300), nullable=False)
    category = Column(String(250), nullable=False)


engine = create_engine(
'sqlite:///item_catalog.db')

Base.metadata.create_all(engine)