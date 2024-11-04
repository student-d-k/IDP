from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine, select
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from idp_classes import *

def get_user_profile(session: Session, user_id: Integer) -> UserProfile:
    stmt = select(UserProfile).where(UserProfile.id == user_id)
    return session.execute(stmt).scalar_one_or_none()
