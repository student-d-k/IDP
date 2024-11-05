from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from model.idp_crud import *

# engine = create_engine('sqlite:///data/idp.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

user_id = "Paulius"
lesson_name = "GitHub Branches"
skill_id = "453"
start_time = datetime.datetime.now() + timedelta(days=2)
end_time = start_time + timedelta(hours=2)

result = create_lesson(session, user_id, lesson_name, skill_id, start_time, end_time)


if result == 'ok':
    print("Lesson created successfully!")
else:
    print(f"Failed to create lesson: {result}")