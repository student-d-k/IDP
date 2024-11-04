import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base

engine = create_engine('sqlite:///data/idp.db', echo=True)
Base = declarative_base()


# vartotojas

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    login = Column('login', String)
    password = Column('password', String)
    ...


# įgūdis

# class UserSkill(Base):
#     __tablename__ = 'user_skill'
#     id = Column(Integer, primary_key=True)
#     value = Column(Integer)
#     name = Column('name', String)


# vartotojo profilis

# class UserProfile(Base):
#     __tablename__ = 'user_profile'
#     user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
#     ...


# užsiėmimas

#class Pratice(Base):
    ...


# vertinimas

# class UserRating?/PracticeRating?(Base):
    ...


Base.metadata.create_all(bind=engine)
