from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from model.idp_crud import *
import datetime

# engine = create_engine('sqlite:///data/idp.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()


def ui_login() -> String:
    # grazina prisiloginusio userio id arba baigia programos darba
    users = get_users(session)
    while True:
        login = input('Prisijungimas: ')
        if login == '':
            exit()
        password = input('Slaptažodis: ')
        for user in users:
            if login == user.id and password == user.password:
                return user.id
        print('Neteisingas prisijungimo vardas arba slaptažodis.')


def ui_profile_choose_profile() -> String:
    # grazina pasirinktą vartotojo id
    users = get_users(session)
    for user in users:
        print(user.id, user.first_name, user.last_name)
    ui = input('Įveskite vartotojo id: ')
    # patikrinti ar toks id egzistuoja, jeigu ne prasom ivesti is naujo
    return ui


def ui_profile_add_lesson(user_id: String):
    # leidžia pridėti užsiėmimą
    # galbūt leidžia pakeisti užsiėmimo laiką
    ...


def ui_profile(user_id: String):
    # parodo vartotojo įgūdžius, aktyvias registracijas, sukurtus užsiėmimus su prisiregistravusių kiekiu
    while True:
        print(user_id)
        skills = get_user_skills(session, user_id)
        for skill in skills:
            rating_name = get_user_skill_rating(session, user_id, skill.id)
            medal_count = get_user_skill_medal_count(session, user_id, skill.id)
            print(f'skill {skill.id} - {rating_name}, {medal_count} medalių')
        ui = input('Pasirinkite veiksmą (1 - kito vartotojo profilis, 2 - sukurti užsiėmimą, b - gryžti): ')
        match ui:
            case '1':
                user_id = ui_profile_choose_profile()
            case '2':
                ui_profile_add_lesson(user_id)
            case 'b':
                return
            case _:
                print('Neteisigai įvedėte')


def ui_enrolments(user_id: str):
    stmt = select(Lesson).join(LessonEnrolment).where(LessonEnrolment.user_id == user_id)
    enrolments = session.execute(stmt).scalars().all()

    if enrolments:
        print("Jūsų esamos registracijos:")
        for lesson in enrolments:
            print(f"Paskaitos ID: {lesson.id}, Pavadinimas: {lesson.name}, Pradžia: {lesson.start}, Pabaiga: {lesson.end}")
    else:
        print("Nesate užsiregistravę į jokias paskaitas.")

    while True:
        action = input("Pasirinkite veiksmą (1 - registracija į paskaitą, 2 - registracijos atšaukimas, b - grįžti")
        
        if action == '1':
            lesson_id = input("Įveskite paskaitos ID, į kurią norite registruotis: ")
            result = enrol_to_lesson(session, user_id, lesson_id)
            print(result)
        
        elif action == '2':
            lesson_id = input("Įveskite paskaitos ID, kurios registraciją norite atšaukti: ")
            result = cancel_enrolment_to_lesson(session, user_id, lesson_id)
            print(result)
        
        elif action == 'b':
            return
        
        else:
            print("Neteisinga įvestis. Prašome bandyti dar kartą.")
            


def enrol_to_lesson(session: Session, user_id: str, lesson_id: int) -> str:
    try:
        # Patikriname, ar paskaita egzistuoja
        lesson = session.execute(select(Lesson).where(Lesson.id == lesson_id)).scalar_one_or_none()
        if not lesson:
            return "Klaida: Tokios paskaitos nėra."

        # Patikriname, ar paskaita jau prasidėjo
        if lesson.start < datetime.datetime.now():
            return "Klaida: Negalima registruotis į paskaitą, kuri jau prasidėjo."

        # Patikriname, ar vartotojas jau yra užsiregistravęs į šią paskaitą
        existing_enrolment = session.execute(select(LessonEnrolment).where(
            LessonEnrolment.user_id == user_id,
            LessonEnrolment.lesson_id == lesson_id
        )).scalar_one_or_none()
        if existing_enrolment:
            return "Klaida: Jūs jau esate užsiregistravęs į šią paskaitą."

        # Patikriname, ar vartotojas neturi kitų registracijų tuo pačiu laiku
        overlapping_enrolments = session.execute(select(LessonEnrolment).join(Lesson).where(
            LessonEnrolment.user_id == user_id,
            Lesson.start <= lesson.end,
            Lesson.end >= lesson.start
        )).scalars().all()
        
        if overlapping_enrolments:
            return "Klaida: Jūs turite kitų registracijų, kurios susikerta su šia paskaita."

        # Įrašome registraciją į LessonEnrolment lentelę
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
        enrolment = session.execute(select(LessonEnrolment).where(
            LessonEnrolment.user_id == user_id,
            LessonEnrolment.lesson_id == lesson_id
        )).scalar_one_or_none()
        if not enrolment:
            return "Jūs nesate užsiregistravęs į šią paskaitą."

        session.delete(enrolment)
        session.commit()
        return "Sėkmingai atšaukėte registraciją."
    except Exception as e:
        session.rollback()
        return f"Klaida: {str(e)}"


def ui_rate_user_skill(user_id: String):
    # isspausdina kokius kitu vartotoju igudzius vartotojas yra vertines
    # leidzia pasirinkti vartotoja, igudi ir ji ivertitni
    ...


current_user_id = ui_login()

ui = '1'
while True:
    match ui:
        case '1':
            ui_profile(current_user_id)
        case '2':
            ui_enrolments(current_user_id)
        case '3':
            ui_rate_user_skill(current_user_id)
        case 'q':
            print('Viso')
            break
        case _:
            print('Neteisigai įvedėte')
    ui = input('Pasirinkite veiksmą (1 - profilis, 2 - registracijos, 3 - vertinimai, q - išeiti): ')

# print(create_lesson(session, 'jons', 'pirma pamoka', 'python', datetime.datetime(2024, 11, 5, 11, 0), datetime.datetime(2024, 11, 5, 12, 0)))
# ui_profile('jons')
