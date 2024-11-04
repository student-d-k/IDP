from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from model import idp_classes, idp_crud

Session = sessionmaker(bind=engine)
session = Session()

print(get_user_profile(session, 1))
