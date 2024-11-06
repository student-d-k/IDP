import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base

engine = create_engine('sqlite:///data/idp.db', echo=False)
Base = declarative_base()


# vartotojas

class User(Base):
    __tablename__ = 'user'
    id = Column('id', String, primary_key=True, nullable=False) # login
    password = Column('password', String, nullable=False)
    first_name = Column('first_name', String, nullable=True)
    last_name = Column('last_name', String, nullable=True)


# įgūdis

class Skill(Base):
    __tablename__ = 'skill'
    id = Column('id', String, primary_key=True, nullable=False)


# vertinimas

class SkillRating(Base):
    __tablename__ = 'skill_rating'
    value = Column(Integer, primary_key=True, nullable=False)
    name = Column('name', String, nullable=False)


# vartotojo įgūdžių vertinimai

class UserSkillRating(Base):
    __tablename__ = 'user_skill_rating'
    user_id = Column(String, ForeignKey('user.id'), primary_key=True, nullable=False)
    skill_id = Column(String, ForeignKey('skill.id'), primary_key=True, nullable=False)
    skill_rating_value = Column(Integer, ForeignKey('skill_rating.value'), nullable=False)
    user_who_rated_id = Column(String, ForeignKey('user.id'), primary_key=True, nullable=False)
    comment = Column(String, nullable=True)


# vartotojo įgūdžių zenkliukai

class UserSkillMedal(Base):
    __tablename__ = 'user_skill_medal'
    user_id = Column(String, ForeignKey('user.id'), primary_key=True, nullable=False)
    skill_id = Column(String, ForeignKey('skill.id'), primary_key=True, nullable=False)
    medal_count = Column(Integer)


# užsiėmimas

class Lesson(Base):
    __tablename__ = 'lesson'
    id = Column('id', Integer, primary_key=True, nullable=False)
    name = Column('name', String, nullable=False)
    teacher = Column(String, ForeignKey('user.id'), nullable=False)
    skill_id = Column(String, ForeignKey('skill.id'), nullable=False)
    start = Column('start', DateTime, nullable=False)
    end = Column('end', DateTime, nullable=False)


# registracija į užsiėmimus

class LessonEnrolment(Base):
    __tablename__ = 'lesson_enrolment'
    lesson_id = Column(Integer, ForeignKey('lesson.id'), primary_key=True, nullable=False)
    user_id = Column(String, ForeignKey('user.id'), primary_key=True, nullable=False)
    created_on = Column('created_on', DateTime, nullable=False)


# prisijungimas prie užsiėmimų

class LessonLog(Base):
    __tablename__ = 'lesson_log'
    lesson_id = Column(Integer, ForeignKey('lesson.id'), primary_key=True, nullable=False)
    user_id = Column(String, ForeignKey('user.id'), primary_key=True, nullable=False)
    logged_on = Column('logged_on', DateTime, nullable=False)
    logged_off = Column('logged_off', DateTime)


# Base.metadata.create_all(bind=engine)
