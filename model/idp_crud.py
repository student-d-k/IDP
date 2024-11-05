from typing import List
from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine, select, insert, or_, and_
from sqlalchemy.orm import declarative_base, sessionmaker, Session
# import datetime
from datetime import datetime, timedelta

if __name__ == "__main__":
    from idp_classes import *
else:
    from model.idp_classes import *

def get_users(session: Session) -> List[User]:
    # pilnas User sąrašas
    stmt = select(User)
    return session.execute(stmt).scalars().all()


def get_user_skills(session: Session, user_id: str) -> List[Skill]:
    # Skill sąrašas, kurių yra įvertinimas arba turi zenkliuku
    stmt = ( 
        select(Skill)
        .outerjoin(UserSkillRating, Skill.id == UserSkillRating.skill_id)
        .outerjoin(UserSkillMedal, Skill.id == UserSkillMedal.skill_id)
        .where((UserSkillRating.user_id == user_id) | (UserSkillMedal.user_id == user_id)))
    return session.execute(stmt).scalars().all()


def get_user_skill_rating(session: Session, user_id: str, skill_id: str) -> str:
    # grąžina vartotojo įgūdžio įvertinimo pavadinimą (None, jeigu nėra)
    stmt = ( 
        select(UserSkillRating)
        .where(UserSkillRating.user_id == user_id and UserSkillRating.skill_id == skill_id))
    ratings = session.execute(stmt).scalars().all()
    if not ratings:
        return None

    avg_rating_value = round(sum(r.skill_rating_value for r in ratings) / len(ratings))
    stmt = select(SkillRating).where(SkillRating.value == avg_rating_value)
    return session.execute(stmt).scalars().one_or_none().name


def get_user_skill_medal_count(session: Session, user_id: str, skill_id: str) -> int:
    # grąžina vartotojo įgūdžio ženkliukų kiekį
    stmt = ( 
        select(UserSkillMedal)
        .where(UserSkillMedal.user_id == user_id and UserSkillMedal.skill_id == skill_id))
    medals = session.execute(stmt).scalars().all()
    if medals is None: 
        return 0
    else:
        return sum(m.medal_count for m in medals)


def get_enrolments(
    session: Session, 
    user_id: str, 
    teacher_id: str, 
    skill_id: str, 
    start_from: datetime.datetime, start_to: datetime.datetime) -> List[Lesson]:
    # Lesson sąrašas pagal filtrą (None reiškia imam viską):
    # user_id - kur vartotojas jau užsiregistravęs
    # teacher_id - užsiėmimai, kurios veda tam tikras mokytojas
    # skill_id - kokį įgudį kelia
    # start_from .. start_to - laiko intervalas, kada prasideda užsiėmimas
    ...


def rate_user_skill(session: Session, user_id: str, user_to_rate_id: str, skill_id: str, rating_value: int) -> str:
    # user_id - vartotojas, kuris vertina
    # user_to_rate_id - vartotojas, kurio įgudį vertina
    # return 'ERR: ...', jeigu klaida
    # jeigu vertinimas, jau buvo, pakeičia rating_value
    ...


def create_lesson(session: Session, user_id: str, name: str, skill_id: str, start: datetime.datetime, end: datetime.datetime) -> str:
    # užsiėmimo sukūrimas
    # return 'ERR: ...', jeigu klaida
    # įrašom į lesson lentelę
    # galima padaryti tikrinimą ar nesikerta su kitais vartotojo užsiėmimais arba registracijomis į užsiėmimus
    all_lessons = session.query(Lesson).all()


    try:
        stmt = insert(Lesson).values(name=name, teacher=user_id, skill_id=skill_id, start=start, end=end)
        for lesson in all_lessons:
            if (start >= lesson.start and start <= lesson.end) or (end >= lesson.start and end <= lesson.end):
                return("ERR: Time for the lesson is taken")
        session.execute(stmt)
        session.commit()
        return 'ok'
    except Exception as e:
        session.rollback()
        return f'ERR: {str(e)}'


def delete_lesson(session: Session, lesson_id: int) -> str:
    # užsiėmimo ištrynimas
    # return 'ERR: ...', jeigu klaida
    # įštrinam iš lesson lentelės ir visas registracijas,
    # jeigu užsiėmimas jau įvyko ar vyksta, tai ištrinti neleidžiama
    ...

def enrol_to_lesson(session: Session, user_id: str, lesson_id: int) -> str:
    # bandymas prisiregistruoti prie užsiėmimo
    # return 'ERR: ...', jeigu klaida
    # įrašom į lesson_enrolment lentelę, created_on = datetime.datetime.now(UTC)
    # pagal laiką primi x bus laikomi sėkmingai užsiregistravę, likę - laukiančiųjų sąraše
    # galima padaryti tikrinimą ar nesikerta su kitomis registracijomis
    ...


def cancel_enrolment_to_lesson(session: Session, user_id: str, lesson_id: int) -> str:
    # bandymas atsisakyti registracijos į užsiėmimą
    # return 'ERR: ...', jeigu klaida
    # ištrinam įrašą iš lesson_enrolment lentelės
    ...


def login_to_lesson(session: Session, user_id: str, lesson_id: int) -> str:
    # bandymas prisijungti prie užsiėmimo (du kartus jungtis negalima arba atsijungti ir vėl prisijungti)
    # prisijungti galima tik +-5 min nuo užsiėmimo pradžios
    # return 'ERR: ...', jeigu klaida
    # įrašom į lesson_log lentelę, jeigu tokio įrašo nėra, logged_on = datetime.datetime.now(UTC)
    ...


def logoff_from_lesson(session: Session, user_id: str, lesson_id: int) -> str:
    # bandymas atsijungti nuo užsiėmimo
    # return 'ERR: ...', jeigu klaida
    # lesson_log.logged_off priskiriam datetime.datetime.now(UTC)
    # pridedam į user_skill_medal.medal_count, jeigu prabuvo 90% laiko paskaitoje
    ...
