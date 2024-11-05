import sqlite3 
  
# Connecting to sqlite 
conn = sqlite3.connect('data/idp.db')
  
cursor = conn.cursor() 

try:

    cursor.execute('''
    INSERT INTO user VALUES 
        ('jons', '', 'Jonas', 'Jonaitis'),
        ('petrs', '', 'Petras', 'Petraitis')
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

    cursor.execute('''
    INSERT INTO user_skill_rating VALUES 
        ('jons', 'Python', 2, 'petrs')
    ''')

    cursor.execute('''
    INSERT INTO user_skill_medal VALUES 
        ('petrs', 'MS Office', 1)
    ''')

    conn.commit()

except Exception as e:

    print(e)

conn.close()
