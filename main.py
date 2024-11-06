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
    print('-'*60)
    print(f'Sveiki atvykę į įgūdžių dalinimosi platformą - IDP')
    print('-'*60)
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


def ui_profile_choose_user_id() -> String:
    # grazina pasirinktą vartotojo id
    users = get_users(session)
    while True:
        for user in users:
            print(user.id, user.first_name, user.last_name)
        ui = input('Įveskite vartotojo id: ').strip().lower()
        # patikrinti ar toks id egzistuoja, jeigu ne prasom ivesti is naujo
        for user in users:
            if ui == user.id.lower():
                return user.id
        print('Klaida: įveskite egzistuojantį vartotojo id')


def ui_profile_add_delete_lesson(user_id: String):
    # leidžia pridėti ištrinti užsiėmimą
    # galbūt leidžia pakeisti užsiėmimo laiką
    while True:
        print('-'*60)
        print(f'{user_id} užsiėmimai')
        print('-'*60)
        lessons = get_enrolments(session, teacher_id=user_id)
        for lesson in lessons:
            print(f'Mano paskaitos: {lesson.id} {lesson.name} - {lesson.skill_id}, pradžia {lesson.start.strftime('%Y %b %d %H:%M')}')
        print('Įveskite (užsiėmimo pavadinimą, įgūdį, pradžios, pabaigos datą-laiką)')
        print('Arba užsiėmimo id, kurį norite ištrinti')
        print('Arba "b" - grįžti')
        action = input('Pvz: Mokau grybauti, Grybai, 2024-11-15 04:00, 2024-11-15 07:00: ')
        try:
            s = action.split(',')
            # gryzti?
            if len(s) == 1 and s[0].strip().lower() == 'b':
                return
            # trinti?
            if len(s) == 1 and s[0].strip().isdigit():
                for l in lessons:
                    if l.id == int(s[0].strip()):
                        print(delete_lesson(session, l.id))
                        break
                else:
                    print(f'Užsimėmimo, kurį norite ištrinti id ({s[0].strip()}) nerastas')
            # pridėti?
            if len(s) == 4:
                print(create_lesson(
                    session, 
                    user_id, 
                    s[0].strip(),
                    s[1].strip(), 
                    datetime.datetime.strptime(s[2].strip(), '%Y-%m-%d %H:%M'),
                    datetime.datetime.strptime(s[3].strip(), '%Y-%m-%d %H:%M')))
        except Exception as e:
            print(f'Kažką neteisingai įvedėte')
            print(f'Klaida: {e}')


def ui_profile_login_lesson(user_id: String):
    # leidžia prisijungti prie paskaitos
    while True:
        print('-'*60)
        print(f'{user_id} užsiėmimai prie kurių galite ar galėsite šiandien jungtis')
        print('-'*60)
        lessons = get_enrolments(
            session, 
            user_id=user_id, 
            start_from=datetime.datetime.now() - datetime.timedelta(minutes=10),
            start_to=datetime.datetime.now() + datetime.timedelta(hours=14))
        for lesson in lessons:
            print(f'Užsiėmimas: {lesson.id} {lesson.name} - {lesson.skill_id}, pradžia {lesson.start.strftime('%Y %b %d %H:%M')}')
        action = input('Įveskite užsiėmimo prie kurio norite prisijungti id arba b - grįžti į profilį: ').strip().lower()
        try:
            # gryzti?
            if action == 'b':
                return
            # prisijungti
            print(login_to_lesson(session, user_id, lesson.id))
        except Exception as e:
            print(f'Kažką neteisingai įvedėte')
            print(f'Klaida: {e}')


def ui_profile_logoff_lesson(user_id: String):
    # randam prisijungima prie paskaitos
    lesson_login = session.execute(select(LessonLog).where(and_(LessonLog.logged_off == None, LessonLog.user_id == user_id))).scalars().all()
    if len(lesson_login) == 0:
        print('Klaida: neturite nuo ko atsijungti')
        return
    action = input(f'Atsijungti iš užsiėmimo {lesson_login[0].lesson_id}? [t/n]: ').strip().lower()
    if action == 't':
        print(logoff_from_lesson(session, user_id, lesson_login[0].lesson_id))
    else:
        print(f'Atsijungimas iš užsiėmimo {lesson_login[0].lesson_id} atšauktas')


def ui_profile(user_id: String):
    # parodo vartotojo įgūdžius, aktyvias registracijas, sukurtus užsiėmimus su prisiregistravusių kiekiu
    main_user_id = user_id
    while True:
        print('-'*60)
        print(f'{user_id} profilis')
        print('-'*60)
        skills = get_user_skills(session, user_id)
        for skill in skills:
            rating_name = get_user_skill_rating(session, user_id, skill.id)
            medal_count = get_user_skill_medal_count(session, user_id, skill.id)
            print(f'Įgūdis {skill.id} - {rating_name}, {medal_count} medalių. Komentarai: {get_user_skill_rating_comments(session, user_id, skill.id)}')
        lessons = get_enrolments(session, teacher_id=user_id)
        for lesson in lessons:
            print(f'Mano paskaitos {lesson.name} - {lesson.skill_id}, pradžia {lesson.start.strftime('%Y %b %d %H:%M')}')
        print('-'*60)
        ui = input('Pasirinkite veiksmą: 1 - kito vartotojo profilis, 2 - sukurti/ištrinti užsiėmimą, 3 - prisijungti, 4 - atsijungti, b - gryžti į pagrindinį meniu: ')
        match ui:
            case '1':
                user_id = ui_profile_choose_user_id()
            case '2':
                ui_profile_add_delete_lesson(main_user_id)
            case '3':
                ui_profile_login_lesson(main_user_id)
            case '4':
                ui_profile_logoff_lesson(main_user_id)
            case 'b':
                return
            case _:
                print('Neteisigai įvedėte')


def ui_enrolments(user_id: str):
    enrolments = get_enrolments(session, user_id=user_id)
    # stmt = select(Lesson).join(LessonEnrolment).where(LessonEnrolment.user_id == user_id)
    # enrolments = session.execute(stmt).scalars().all()
    print('-'*60)
    print(f'{user_id} registracijos')
    print('-'*60)

    if len(enrolments) > 0:
        print("Jūsų esamos registracijos:")
        for lesson in enrolments:
            print(f"Paskaitos ID: {lesson.id}, Pavadinimas: {lesson.name}, Pradžia: {lesson.start}, Pabaiga: {lesson.end}")
    else:
        print("Nesate užsiregistravę į jokias paskaitas.")
    print('-'*60)

    lessons = session.execute(select(Lesson).where(Lesson.start > datetime.datetime.now() - datetime.timedelta(minutes=10))).scalars().all()
    if len(lessons) > 0:
        print('Galimi užsiėmimai:')
        for lesson in lessons:
            print(f'Užsiėmimo id: {lesson.id}, pavadinimas: {lesson.name}, pradžia: {lesson.start}, pabaiga: {lesson.end}')
    else:
        print('Nėra užsiėmimų į kuriuos galite registruotis')

    while True:
        action = input("Pasirinkite veiksmą (1 - registracija į paskaitą, 2 - registracijos atšaukimas, b - grįžti: ")
        
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
    print('-'*60)
    print(f'{user_id} vertinimai')
    print('-'*60)
    users = get_users(session)
    while True:
        for u in users:
            stmt = ( 
                select(UserSkillRating)
                .where((UserSkillRating.user_who_rated_id == user_id) & (UserSkillRating.user_id == u.id)))
            ratings = session.execute(stmt).scalars().all()
            if len(ratings) > 0:
                for r in ratings:
                    stmt = select(SkillRating).where(SkillRating.value == r.skill_rating_value)
                    s = session.execute(stmt).scalars().one_or_none().name
                    print(f'Jūs įvertinote {u.id} {u.first_name} įgūdį {r.skill_id} - {s}')
            else:
                print(f'{u.id} {u.first_name} neturi jūsų vertinimų')
        print('-'*60)
        print('Pasirinkite veiksmą: vartotojo_id, įgūdis, vertinimas(1..3), komentaras(neprivalomas) arba b - grįžti')
        action = input('Pvz. jon, Python, 1, nieko nesupranta tik daug kalba: ').strip()
        if action == 'b':
            return
        try:
            s = action.split(',')
            if len(s) == 3 or len(s) == 4:
                action_id, action_skill, action_value = s[0].strip(), s[1].strip(), s[2].strip()
                if len(s) == 4:
                    action_comment = s[3].strip()
                else:
                    action_comment = None
                if action_id in [user.id for user in users]:
                    print(rate_user_skill(session, user_id, action_id, action_skill, action_value, action_comment))
                else:
                    print('Klaida: tokio vartotojo id nėra')
            else:
                print(f'Kažką neteisingai įvedėte')
        except Exception as e:
            print(f'Kažką neteisingai įvedėte')
            print(f'Klaida: {e}')


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
