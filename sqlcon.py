import mysql.connector as m

conn = m.connect(
    host='localhost',
    user='root',
    password='password',
    database='ChemLib'
)

cur = conn.cursor()

def Titles():
    cur.execute("SELECT title from wiki_data")
    titles = []
    for i in cur.fetchall():
        titles.append(i[0])
    return titles

def WikiData(title):
    cur.execute("SELECT * FROM wiki_data WHERE title='{}' ".format(title))
    record = cur.fetchone()
    if record == ():
        return None
    else:
        return record

def UserVerification(username,password):
    cur.execute('SELECT * FROM userauth')
    a = cur.fetchall()
    if (username,password) in a:
        return True
    else:
        return False

def AddReaction(title,overview,image):
    if image == "":
        cur.execute("INSERT INTO wiki_data(title,overview) values('{}','{}')".format(title,overview))
    else:
        cur.execute("INSERT INTO wiki_data(title,overview,image_path) values('{}','{}','{}')".format(title,overview,image))
    conn.commit()

def AddUser(user,passw):
    cur.execute("INSERT INTO userauth values('{}','{}')".format(user,passw))
    conn.commit()
    print("Admin User added successfully")

def AddChemicalData(data):
    query = f"INSERT INTO chemicals VALUES("
    AllData = data
    for i in AllData:
        if type(i) == int or type(i) == float:
            query = query+str(i)+","
        else:
            query = query+"'{}'".format(i)+','
    query = query[:-1] + ");"
    cur.execute(query)
    conn.commit()

def GetChemicalData(a):
    query = f"SELECT * FROM chemicals WHERE formula='{a}' OR common='{a}' OR iupac='{a}' OR CAS='{a}' OR smiles='{a}' OR pubchemid='{a}'"
    cur.execute(query)
    result = cur.fetchone()
    if result:
        result1 = list(result)
        if result1[8].title() == "Yes":
            result1[8] = True
        elif result1[8].title() == "False":
            result1[8] = False
        else:
            result1[8] = "No Data"
        return result
    else:
        return None
