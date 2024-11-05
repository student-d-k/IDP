import sqlite3 
  
# Connecting to sqlite 
conn = sqlite3.connect('data/idp.db')
  
cursor = conn.cursor() 

try:

    cursor.execute('DELETE FROM user_skill_medal')
    cursor.execute('DELETE FROM user_skill_rating')
    cursor.execute('DELETE FROM user')
    cursor.execute('DELETE FROM skill')
    cursor.execute('DELETE FROM skill_rating')
    
    # šitos lenteles pildomos rankiniu būdu per sql ar db viewer

    cursor.execute('''
    INSERT INTO user VALUES 
        ('ais', '', 'Aistė', 'S.'),
        ('dk', '', 'Daumantas', 'K.'),
        ('ks', '', 'Karolis', 'S.'),
        ('pm', '', 'Paulius', 'M.'),
        ('rob', '', 'Robertas', 'L.')
    ''')

    cursor.execute('''
    INSERT INTO skill VALUES 
        ('Python'),
        ('MS Office')
    ''')

    cursor.execute('''
    INSERT INTO skill_rating VALUES 
        (1, 'Pradedantysis'),
        (2, 'Vidutinio lygio'),
        (3, 'Ekspertas')
    ''')

    # nuo čia optional, šitos lentelės pildomos per UI

    cursor.execute('''
    INSERT INTO user_skill_rating VALUES 
        ('ais', 'Python', 1, 'dk'),
        ('dk', 'Python', 1, 'dk')
    ''')

    cursor.execute('''
    INSERT INTO user_skill_medal VALUES 
        ('ais', 'Python', 2),
        ('dk', 'MS Office', 10)
    ''')

    conn.commit()

except Exception as e:

    print(e)

conn.close()
