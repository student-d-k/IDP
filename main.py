# poetry init 
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
    # Parodo konkretaus vartotojo profilį su įgūdžiais, aktyviomis registracijomis ir sukurtų užsiėmimų duomenimis
    print(f"\nVartotojo ID: {user_id}")
    
    # 1. Rodyti tik konkretaus vartotojo įgūdžius
    print("Įgūdžiai:")
    skills = session.query(Skill).join(UserSkillMedal, Skill.id == UserSkillMedal.skill_id)\
                                 .filter(UserSkillMedal.user_id == user_id).all()
    
    seen_skills = set()
    for skill in skills:
        skill_id = getattr(skill, "id", None)
        if skill_id and skill_id not in seen_skills:
            seen_skills.add(skill_id)
            skill_name = skill.id
            rating_name = get_user_skill_rating(session, user_id, skill_id)
            medal_count = get_user_skill_medal_count(session, user_id, skill_id)
            print(f'Įgūdis: {skill_name} - {rating_name}, Medalių skaičius: {medal_count}')
    
    # 2. Rodyti aktyvias registracijas
    print("\nAktyvios Registracijos:")
    enrolments = get_enrolments(session, user_id)
    if enrolments:
        for enrolment in enrolments:
            print(f"Užsiėmimas: {enrolment.lesson_id} - Data: {enrolment.date}, Statusas: {enrolment.status}")
    else:
        print("Nėra aktyvių registracijų")
    
    # 3. Rodyti sukurtus užsiėmimus su prisiregistravusiųjų kiekiu
    print("\nSukurti Užsiėmimai:")
    lessons = session.query(Lesson).filter_by(teacher=user_id).all()
    for lesson in lessons:
        enrolment_count = session.query(LessonEnrolment).filter_by(lesson_id=lesson.id).count()
        print(f"Užsiėmimas: {lesson.name} - Pradžia: {lesson.start}, Pabaiga: {lesson.end}, Prisiregistravusių: {enrolment_count}")   


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
