import chem
from PIL import Image
import sqlcon
from datetime import datetime
import pickle
import csv
import matplotlib.pyplot as plt
import os


search_prompt = """
Chemical Search can be done using the following ways
* Search using the name of the compound / element
* Search using the formula of the compound or the symbol of the element
* Search using CAS identifier
* Search using PubChem CID, prefixed by 'PubChem='
* Search using SMILES, prefixed by 'SMILES='
* Search using InChl name, prefixed by 'InChl=1S/'
* Search using InChI key, prefixed by 'InChIKey='

Enter Search Query: """

def search_comp():
    search_inp = input(search_prompt)
    search_inp = search_inp.lower()
    ret = chem.process_data(search_inp)
    if ret:
        el = chem.is_element(ret[0]['formula'])
        response = f'''
    =======================================================================================================================
    {"Element" if el else "Compound"} Information:

    {"Element" if el else "Compound"} Name: {ret[0]['common'].title()}
    {"Element Symbol" if el else "Compound Formula"} : {ret[0]['formula']}
    {"Compound IUPAC Name: "+ret[0]['iupac'] if not el else ''}

    Physical Properties:
    Molar Mass: { '{:.2f}'.format(ret[0]["MW"]) } g/mol
    Boiling Point: { ret[3]['BP'] if type(ret[3]['BP'])==str else str(ret[3]['BP'])+"° K"}
    Melting Point: { ret[3]['MP'] if type(ret[3]['MP'])==str else str(ret[3]['MP'])+"° K"}
    Flash Point: { ret[3]['flash'] if type(ret[3]['flash'])==str else str(ret[3]['flash'])+"° K"}

    Chemical Safety Properties:
    Carcinogenicity: { "No Info" if ret[2]['carcinogen']['International Agency for Research on Cancer'] == "Unlisted" else ret[2]['carcinogen']['International Agency for Research on Cancer'] }
    Chemical can be absorbed through Skin: { ret[2]['skin'] }

    Identifiers:
    CAS: { ret[1]['CAS']}
    PubChem: {ret[1]['pubchemid']}

    ========================================================================================================================
    '''
        print(response)
        img_ch = input("Do you wish to see the structure of the compound/element (y or n): ")
        if img_ch == 'y': 
            image = Image.open(ret[4]["img"])
            image.show()
    else:
        print("No such Entity Found")

def list_all_rxns():
    titles = sqlcon.Titles()
    if len(titles) == 0:
        print("There are no Reactions present in Database")
    c=1
    for i in titles:
        print(str(c)+")"+i)
        c=c+1

def search_rxn():
    inp = input("Enter reaction name to search: ")
    dat = sqlcon.WikiData(inp)
    found = False
    if dat:
        found = True
        print("Name of Reaction: "+dat[1]) 
        print('\n')
        print("Overview: "+dat[2]) 
        print("\n")
        im = Image.open(dat[3])
        im.show()
    else:
        words = inp.split()
        for i in sqlcon.Titles():
            for word in words:
                if word.lower() in i.lower():
                        found = True
                        print("Closest Title to your search: "+i)
                        dat = sqlcon.WikiData(i)
                        print("Name of Reaction: "+dat[1]) 
                        print('\n')
                        print("Overview: "+dat[2])
                        print("\n")
                        im = Image.open(dat[3])   
                        im.show()
                        break
    if not found:
        print("Reaction not found")

def ChangeLog(message):
    timedate = datetime.now()
    t_string = timedate.strftime(r"%d/%m/%Y %H:%M:%S")
    log = message + t_string
    f = open("config.bin",'ab')
    pickle.dump(log,f)
    f.close()

def LogView():
    try:
        with open('config.bin', 'rb') as f:
            logs = []
            while True:
                a = pickle.load(f)
                logs.append(a)
    except EOFError:
        print('\n')
        for i in logs:
            print(i)
        print("No more Logs")


def EnterChemicalData():
    prompts='''Enter Chemical Formula:
Enter Chemical Common Name:
Enter Chemical IUPAC Name:
Enter Molecular Weight:
Enter CAS ID:
Enter Smiles:
Enter PubChemID:
Enter Carcinogenic Property:
Whether Substance can get absorbed through Skin (Yes/No): 
Enter Boiling Point ( In Kelvin Units ): 
Enter Melting Point ( In Kelvin Units ):
Enter Flash Point (In Kelvin Units ):
Enter Path for Structure Image :
Enter Alternate Terms for the Chemical: '''
    data = []
    c=0
    for i in prompts.split("\n"):
        if c in [3,9,10,11]:
            while True:
                try:
                    j = float(input(i))
                    data.append(j)
                    break
                except ValueError:
                    print("Expected a number, try again")
        elif c == 12:
            while True:
                j = input(i)
                if os.path.exists(j):
                    data.append(j)
                    break
                else:
                    print("Image does not exist, try again")
        else:
            j = input(i)
            data.append(j)

        c=c+1

    sqlcon.AddChemicalData(data)
    ChangeLog("New Chemical Added at: ")
    print("Entity added successfully")

#credentials user/pass : admin/admin

def adminlogin():
    username = input("Enter Username: ")
    password = input("Enter Password: ")
    whether_admin = sqlcon.UserVerification(username,password)
    if whether_admin:
        ChangeLog("Admin User {} logged in at: ".format(username))
        admin_prompt = '''
a) Enter data for a new reaction
b) Enter data for a new chemical entity
c) View Change Log of Database
d) Add New Users to the Application
e) Quit Admin Prompt

:
'''
        choice = input(admin_prompt)
        while choice != 'e':
            if choice == 'a':
                title = input("Enter Name of the Reaction: ")
                overview = input("Enter overview details about the Reaction:\n")
                image_path=''
                while True:
                    image_path = input("Enter Path of reference image for the reaction : ")
                    if os.path.exists(image_path):
                        break
                    else:
                        print("image does not exist, try again")
                sqlcon.AddReaction(title,overview,image_path)
                ChangeLog("Reaction Data added by {} at: ".format(username))
            elif choice == 'b':
                EnterChemicalData()
            elif choice == 'c':
                LogView()
            elif choice == 'd':
                n_user = input("New Username: ")
                n_pass = input("New Password: ")
                sqlcon.AddUser(n_user,n_pass)
                ChangeLog("Admin User added by {} at: ".format(username))
            else:
                print("Invalid Option, Try again")
            choice = input(admin_prompt)
    else:
        print("Invalid Username or Password")
        
def csvwriter(data):
    filename = input("Enter the location/name of the CSV file: ")
    f = open(filename,'a+')
    writer = csv.writer(f)
    heading = [["Chemical Formula","Common Name","IUPAC Name", "Molecular Weight"],
               ["CAS Number","SMILES","PubChemID"],
               ["Carcinogenic Property","Skin Absorbance"],
               ["Boiling Point","Melting Point","Flash Point"]]
    c=0
    for i in heading:
        writer.writerow(i)
        writer.writerow(data[c].values())
        c=c+1
    f.close()

def textwriter(data):
    filename = input("Enter the location/name of the Text file: ")
    f = open(filename,'a+')
    heading = ['"Chemical Formula","Common Name","IUPAC Name", "Molecular Weight"',
               '"CAS Number","SMILES","PubChemID"',
               '"Carcinogenic Property","Skin Absorbance"',
               '"Boiling Point","Melting Point","Flash Point"']
    c=0
    for i in heading:
        f.write(i)
        dat = "".join(',',data[c].values())
        f.write("\n")
        f.write(dat)
        f.write("\n")
        c=c+1
    f.close()

def ChemInfoWriter():
    a = input("Enter Search Query for Compound/Element: ")
    data = chem.process_data(a)
    while True:
        choice = input("a) For writing into a csv file, b) For writing into a text file: ")
        if choice == "a":
            csvwriter(data)
            print("Data Written")
            break
        elif choice == "b":
            textwriter(data)
            print("Data Written")
            break
        else:
            print("Invalid Choice, retry again")

def DataVisualiser():
    while True:
        start = int(input("Enter Starting Atomic Number:"))
        stop = int(input("Enter Ending Atomic Number: "))
        if start in range(1,119) and stop in range(1,119):
            break
        else:
            print("Invalid Atomic Number, Try Again")
    l = chem.datatrends(start,stop)
    y = l[0]
    x = list(range(start,stop+1))
    plt.plot(x,y)
    plt.xlabel(" Atomic Number ")
    plt.ylabel(l[1])
    plt.title(" Data Visualization ")
    plt.show()

greetings="""
Welcome to ChemLib
Choose your option to continue from below

1) Search info for a Chemical compound / Element
2) Search for information about an reaction
3) List all reactions present in the database
4) Visualise data using graphs
5) Write Chemical / Reaction data to a text file or csv file
6) Admin Prompt
7) Quit

"""

def cont():
    inp = input("Would you like to continue y/n: ")
    if inp == 'y':
        return True
    else:
        return False

def menu():
    print(greetings)
    op = int(input("Enter Your Choice: "))
    while op != 7:
        if op == 1:
            search_comp()
            a = cont()
            if not a:
                break
        elif op == 2:
            search_rxn()
            a = cont()
            if not a:
                break
        elif op == 3:
            list_all_rxns()
            a = cont()
            if not a:
                break
        elif op == 4:
            DataVisualiser()
            a = cont()
            if not a:
                break
        elif op == 5:
            ChemInfoWriter()
            a = cont()
            if not a:
                break
        elif op == 6:
            adminlogin()
            a = cont()
            if not a:
                break
        else:
            print("Input Not Recognized, Try Again")
            op = int(input("Enter Your Choice: "))
        os.system('clear')
        print(greetings[63:])
        op = int(input("Enter Your Choice: "))    

try:
    menu()
except ValueError:
    print("Invalid Input, Try Again")
    menu()
except KeyboardInterrupt:
    print("\nProgram Stopped")
