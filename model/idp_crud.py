from typing import List
from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine, select, and_, insert, delete, or_
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
        select(Skill).distinct()
        .outerjoin(UserSkillRating, Skill.id == UserSkillRating.skill_id)
        .outerjoin(UserSkillMedal, Skill.id == UserSkillMedal.skill_id)
        .where((UserSkillRating.user_id == user_id) | (UserSkillMedal.user_id == user_id)))
    return session.execute(stmt).scalars().all()


def get_user_skill_rating(session: Session, user_id: str, skill_id: str) -> str:
    # grąžina vartotojo įgūdžio įvertinimo pavadinimą (None, jeigu nėra)
    stmt = ( 
        select(UserSkillRating)
        .where((UserSkillRating.user_id == user_id) & (UserSkillRating.skill_id == skill_id)))
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
        .where((UserSkillMedal.user_id == user_id) & (UserSkillMedal.skill_id == skill_id)))
    medals = session.execute(stmt).scalars().all()
    if medals is None: 
        return 0
    else:
        return sum(m.medal_count for m in medals)


def get_enrolments(
    session: Session, 
    user_id: str = None, 
    teacher_id: str = None, 
    skill_id: str = None, 
    start_from: datetime.datetime = None, 
    start_to: datetime.datetime = None
) -> List[Lesson]:
    # Lesson sąrašas pagal filtrą (None reiškia imam viską):
    # user_id - kur vartotojas jau užsiregistravęs
    # teacher_id - užsiėmimai, kurios veda tam tikras mokytojas
    # skill_id - kokį įgudį kelia
    # start_from .. start_to - laiko intervalas, kada prasideda užsiėmimas
    stmt = select(Lesson).join(LessonEnrolment, Lesson.id == LessonEnrolment.lesson_id)
    # filtrai
    filters = []
    if user_id is not None:
        filters.append(LessonEnrolment.user_id == user_id)
    if teacher_id is not None:
        filters.append(Lesson.teacher == teacher_id)
    if skill_id is not None:
        filters.append(Lesson.skill_id == skill_id)
    if start_from is not None:
        filters.append(Lesson.start >= start_from)
    if start_to is not None:
        filters.append(Lesson.start <= start_to)
    if filters:
        stmt = stmt.where(and_(*filters))
    return session.execute(stmt).scalars().all()


def rate_user_skill(session: Session, user_id: str, user_to_rate_id: str, skill_id: str, rating_value: int) -> str:
    # user_id - vartotojas, kuris vertina
    # user_to_rate_id - vartotojas, kurio įgudį vertina
    # return 'ERR: ...', jeigu klaida
    # jeigu vertinimas, jau buvo, pakeičia rating_value
    user_to_rate = session.query(User).filter(User.id == user_to_rate_id).first()
    if not user_to_rate:
        return 'ERR: Vartotojas, kurio įgūdis vertinamas yra nerastas.'
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        return 'ERR: Vartotojas kuris vertina nerastas.'
    existing_rating = session.query(UserSkillRating).filter(UserSkillRating.user_id == user_to_rate_id, UserSkillRating.skill_id == skill_id, UserSkillRating.user_who_rated_id == user_id).first()
    try:
        if existing_rating:
            existing_rating.skill_rating_value = rating_value
            session.commit()
            return 'Vertinimas atnaujintas.'
        else:
            new_rating = UserSkillRating(user_id=user_to_rate_id, skill_id=skill_id, skill_rating_value=rating_value, user_who_rated_id=user_id)
            session.add(new_rating)
            session.commit()
            return 'Vertinimas pridėtas.'
    except Exception as e:
        session.rollback()
        return f'ERR: {str(e)}'


def create_lesson(session: Session, user_id: str, name: str, skill_id: str, start: datetime.datetime, end: datetime.datetime) -> str:
    # užsiėmimo sukūrimas
    # return 'ERR: ...', jeigu klaida
    # įrašom į lesson lentelę
    # galima padaryti tikrinimą ar nesikerta su kitais vartotojo užsiėmimais arba registracijomis į užsiėmimus
    conflicting_lessons = (
        session.query(Lesson)
        .filter(
            (Lesson.teacher == user_id) & 
            ((Lesson.start <= start) & (Lesson.end >= start) | 
             (Lesson.start <= end) & (Lesson.end >= end))
        )
        .all()
    )
    if conflicting_lessons:
        return 'Klaida: Šiuo laiku jau turite sukurtų užsimėminų'
    try:
        stmt = insert(Lesson).values(name=name, teacher=user_id, skill_id=skill_id, start=start, end=end).returning(Lesson.id)
        ex_result = session.execute(stmt)
        new_lesson_id = ex_result.scalar_one()
        stmt = insert(LessonEnrolment).values(
            lesson_id=new_lesson_id, 
            user_id=user_id, 
            created_on=datetime.datetime.strptime('2049-12-30', '%Y-%m-%d')
        )
        session.execute(stmt)
        session.commit()
        return 'ok'
    except Exception as e:
        session.rollback()
        return f'Klaida: {str(e)}'


def delete_lesson(session: Session, lesson_id: int) -> str:
    # užsiėmimo ištrynimas
    # return 'ERR: ...', jeigu klaida
    # įštrinam iš lesson lentelės ir visas registracijas,
    # jeigu užsiėmimas jau įvyko ar vyksta, tai ištrinti neleidžiama
    lesson = session.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        return 'ERR: Užsiėmimas nerastas.'
    now = datetime.datetime.now()
    if lesson.start <= now <= lesson.end:
# !!! @Aistė čia netiesa, čia sąlyga, kad užsiėmimas jau vyksta, bet nereiškia, kad užsiėmimas jau įvyko        
        return 'ERR: Užsiėmimas vis dar vyksta arba jau įvyko.'
    try:
        session.execute(delete(LessonEnrolment).where(LessonEnrolment.lesson_id == lesson_id))
        session.execute(delete(Lesson).where(Lesson.id == lesson_id))
        session.commit()
        return 'Užsiėmimas ištrintas.'
    except Exception as e:
        session.rollback()
        return f'ERR: {str(e)}'    


def enrol_to_lesson(session: Session, user_id: str, lesson_id: int) -> str:

    try:
        lesson = session.execute(select(Lesson).where(Lesson.id == lesson_id)).scalar_one_or_none()
        if not lesson:
            return "Klaida: Tokios paskaitos nėra."

        if lesson.start < datetime.datetime.now():
            return "Klaida: Negalima registruotis į paskaitą, kuri jau prasidėjo."

        existing_enrolment = session.execute(select(LessonEnrolment).where(
            LessonEnrolment.user_id == user_id,
            LessonEnrolment.lesson_id == lesson_id
        )).scalar_one_or_none()
        if existing_enrolment:
            return "Klaida: Jūs jau esate užsiregistravęs į šią paskaitą."

        overlapping_enrolments = session.execute(select(LessonEnrolment).join(Lesson).where(
# @ manau neteisinga sąlyga, turėtų būti:
# LessonEnrolment.user_id == user_id IR (
# Lesson.start <= lesson.start <= Lesson.end ARBA
# Lesson.start <= lesson.end <= Lesson.end)
            LessonEnrolment.user_id == user_id,
            Lesson.start <= lesson.end,
            Lesson.end >= lesson.start
        )).scalars().all()
        
        if overlapping_enrolments:
            return "Klaida: Jūs turite kitų registracijų, kurios susikerta su šia paskaita."

        new_enrolment = LessonEnrolment(
            lesson_id=lesson_id,
            user_id=user_id,
            created_on=datetime.datetime.now(datetime.timezone.utc)  # Naudojame UTC laiką
        )
        session.add(new_enrolment)
        session.commit()
        return "Sėkmingai užsiregistravote į paskaitą."
    
    except Exception as e:
        session.rollback()
        return f"Klaida: {str(e)}"


def cancel_enrolment_to_lesson(session: Session, user_id: str, lesson_id: int) -> str:
    try:
        # patikrinam ar registracija egzistuoja
        enrolment = session.execute(select(LessonEnrolment).where(
            LessonEnrolment.user_id == user_id,
            LessonEnrolment.lesson_id == lesson_id
        )).scalar_one_or_none()
        if not enrolment:
            return "Klaida: jūs nesate užsiregistravęs į šią paskaitą."
        # patikrinam ar paskaita ne paties vartotojo sukurtas uzsiemimas
        self_enrolment = session.execute(
            select(LessonEnrolment)
            .join(Lesson)
            .where(
                LessonEnrolment.user_id == user_id,
                LessonEnrolment.lesson_id == lesson_id,
                Lesson.teacher_id == user_id
            )
        ).scalar_one_or_none()
        if not self_enrolment:
            return 'Klaida: negalite atšaukti registracijos į savo užsiėmimą. Ištrinkite užsiėmimą'

        # trinam
        session.delete(enrolment)
        session.commit()
        return "Sėkmingai atšaukėte registraciją."
    except Exception as e:
        session.rollback()
        return f"Klaida: {str(e)}"


def login_to_lesson(session: Session, user_id: str, lesson_id: int) -> str:
    # bandymas prisijungti prie užsiėmimo (du kartus jungtis negalima arba atsijungti ir vėl prisijungti)
    # prisijungti galima tik +-5 min nuo užsiėmimo pradžios
    # return 'ERR: ...', jeigu klaida
    # įrašom į lesson_log lentelę, jeigu tokio įrašo nėra, logged_on = datetime.datetime.now(UTC)
    try:
        # err check 1
        lesson = session.execute(select(Lesson).where(Lesson.id == lesson_id)).scalars().all()
        if not lesson:
            return f'Klaida: tokios paskaitos ({lesson_id}) nėra'
        # err check 2
        lesson_login = session.execute(
            select(LessonLog)
            .where((LessonLog.lesson_id == lesson_id) & (LessonLog.user_id == user_id))
        ).scalars().all()
        if lesson_login:
            return f'Klaida: jau esate prisijungę prie paskaitos {lesson_id}'
        # err check 3
        enrolments = get_enrolments(session, user_id=user_id)
        for e in enrolments:
            if e.id == lesson_id:
                current_lesson = e
                break
        else:
            return f'Klaida: jūs nesate prisiregistravę prie paskaitos {lesson_id}'
        # check uzsiemimo pradzios laikas
        if (current_lesson.start - datetime.timedelta(minutes=5) > datetime.datetime.now() or 
           current_lesson.start + datetime.timedelta(minutes=5) < datetime.datetime.now()):
            return f'Klaida: negalite prisijungti prie paskaitos {lesson_id}, per anksti arba pavėlavote'
        # prisijungimas
        lesson_log = LessonLog(
            lesson_id=lesson_id,
            user_id=user_id,
            logged_on=datetime.datetime.now(datetime.timezone.utc)
        )
        session.add(lesson_log)
        session.commit()
        return f'Sėkmingai prisijungėte prie paskaitos {lesson_id}'
    except Exception as e:
        session.rollback()
        return f"Klaida: {str(e)}"


def logoff_from_lesson(session: Session, user_id: str, lesson_id: int) -> str:
    # bandymas atsijungti nuo užsiėmimo
    # return 'ERR: ...', jeigu klaida
    # lesson_log.logged_off priskiriam datetime.datetime.now(UTC)
    # pridedam į user_skill_medal.medal_count, jeigu prabuvo 90% laiko paskaitoje
    try:
        # randam prisijungima prie paskaitos
        lesson_login = session.execute(
            select(LessonLog)
            .where((LessonLog.lesson_id == lesson_id) & (LessonLog.user_id == user_id))
        ).scalars().all()
        if not lesson_login:
            return f'Klaida: negalite atsijungti, nes nesate prisijungęs prie paskaitos {lesson_id}'
        if lesson_login[0].logged_off is None:
            lesson_login[0].logged_off = datetime.datetime.now(datetime.timezone.utc)
            session.commit()
            lesson = session.query(Lesson).filter(Lesson.id == lesson_id).one_or_none()
            # check
            if lesson.end + datetime.timedelta(minutes=5) < datetime.datetime.now():
                return f'Sėkmingai atsijungėte iš paskaitos {lesson_id}, bet ženkliuko negavote, nes pramiegojote paskatos pabaigą'
            # atrodo viskas ok
            # zenkliukai
            lesson_duration = (lesson.end - lesson.start).total_seconds()
            session_duration = (lesson_login[0].logged_off - lesson_login[0].logged_on).total_seconds()
            if session_duration >= 0.9 * lesson_duration:
                # pridedam ženkliuką
                medals = session.execute(
                    select(UserSkillMedal)
                    .where((UserSkillMedal.user_id == user_id) & (UserSkillMedal.skill_id == lesson.skill_id))
                ).scalars().all()
                if len(medals) == 0:
                    medal_count = 1
                else:
                    medal_count = medals[0].medal_count + 1
                medal = UserSkillMedal(user_id=user_id, skill_id=lesson.skill_id, medal_count=medal_count)
                session.add(medal)
                session.commit()
                return f'Sėkmingai atsijungėte iš paskaitos {lesson_id} ir gavote ženkliuką (+)'
            else:
                return f'Sėkmingai atsijungėte iš paskaitos {lesson_id}, bet ženkliuko negavote, nes dalyvavote per mažai paskaitos laiko'
        else:
            return f'Klaida: negalite atsijungti, nes jau sykį atsijungėte iš paskaitos {lesson_id}'
    except Exception as e:
        session.rollback()
        return f"Klaida: {str(e)}"
