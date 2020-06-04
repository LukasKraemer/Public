# HA - Tool version 2.0b
#geschrieben von Lukas Krämer
# Ohne Haftung
# 2020

from tkinter import * 
from tkinter import ttk
import time 
import pandas as pd 
import sqlalchemy 
import pymysql
import fnmatch
import sys 
import shutil
import ctypes 
import threading 
from sys import platform 
import os, subprocess 
from datetime import datetime
import configparser
import logging




#Globale Variablen
config = configparser.ConfigParser() #config tool
now = datetime.now() # aktuelle uhrzeit
fred = threading.Thread() #prozessverwaltung
sperre = threading.Lock() # prozesssperre
login_db = str() #überprüfung ob Nutzer an der Datenbank angemeldet ist
engine= None #Datenbankverbindung
config.read("config.ini") # Config  File

#Tabellennamen und Pfad
raw_data_tabelle = config.get("table", "raw_data_tabelle")
sprit_tabelle = config.get("table", "sprit_tabelle")
uebersichts_tabelle = config.get("table", "uebersichts_tabelle")
path = config.get("system", "path")
todo_trips= list()

#logger - noch nicht eingebaut
logging.basicConfig(filename='app.log', filemode='a', format=f'%(name)s - {platform} - {now.strftime("%d/%m/%Y, %H:%M:%S")} - %(levelname)s - %(message)s')
#logging.warning("fehler")


def is_admin():
    '''überprüft ob man in Windows als admin angemeldet ist'''
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def prompt_sudo():
    '''überprüft ob man in Linux admin ist'''
    ret = 0
    if os.geteuid() != 0:
        print("Bitte bitte mit root-Rechten anmelden!")
        msg = "[sudo] password for %u:"
        ret = subprocess.check_call("sudo -v -p '%s'" % msg, shell=True)
    return ret

def plattform_check():
    '''überprüft welches Betriebsystem installeirt ist und ob man Admin Rechte hat'''
    global path
    if platform == "linux" or platform == "linux2":
        if path == "nicht gesetzt":
            path= "/var/ha-tools/"
        if prompt_sudo() != 0:
            print("kein admin")()
            exit()
        

    elif platform == "win32":
        if path == "nicht gesetzt":
            path= "C:/ha-tools/"
        #ADMINRECHTE WERDEN NCIHT BENÖTIGT, falls doch bitte ausklammern
        #if is_admin():
        #    print("admin")
        #else:
        #    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        #    exit()

    else:
        print ("unbekanntes System")
        time.sleep(5)
        exit()
   
    if not(os.path.isdir(path)):
        print("kein Ordner vorhanden - Ordner wird erstellt")
        os.makedirs(path)

def login_value(create="No"):
    '''Verbindung zur Datenbank wird hergestellt und ein kleiner log eintrag auf die DB gemacht'''
    global login_db
    global engine
    global now

    if create != "No":
        if User.get() != "":
            Nutzername= (User.get())
        else:
            Nutzername="NONE"
            print("Kein Benutzername festgelegt")

        if Pass.get() != "":  
            Passwort = (Pass.get())
        else:
            Passwort="NONE"
            print("Passwort fehlt")
            
        if anschluss.get() != "":
            Port= str(anschluss.get())
        else:
            Port= "3306"
        
        if DB_schema.get() != "":
            Schema= (DB_schema.get())
        else:
            Schema = "car"
            
        SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{Nutzername}:{Passwort}@localhost:{Port}/{Schema}'# [treiber]://[benutzername][passwort]@[IP]/[Schema in DB]
        engine = sqlalchemy.create_engine(SQLALCHEMY_DATABASE_URI)#herstellen der DB Verbindung
        print(SQLALCHEMY_DATABASE_URI)
    else:
        print(engine)
 
    try: 
        data = {'nutzername': [Nutzername], "Zeit" : [now.strftime("%d/%m/%Y, %H:%M:%S")], "Remote" : ip.get(), "OS": [platform]} 
        logger = pd.DataFrame(data)
        logger.to_sql("loger", con=engine, if_exists='append')
        login_db= True
    except Exception as e:
        print (e)
        login_db=False
    
    if login_db == True:
            loginsuccess.set("ANGEMELDET")
            label_loginsuccess.config(bg='green')
            root.update()
            return engine
    else:
        loginsuccess.set("Fehler!")
        root.update()     
    
def progressBarbuilder_uebersicht(prozess):
    '''Funktion ist nicht eingebaut - später soll für jeden Prozess eine Statusleiste erstellt werden'''
    i= 0
    statusleiten = []
    for i in range (prozess):
        statusleiten.append(progressBarpro = ttk.Progressbar(progesFrame, orient="horizontal", length=400))
        statusleiten[i].grid(column = 1, row = 15+i, padx=5, pady=5)
        statusleiten[i]['value']=0

def lasttrip(tabellenname, tripid= "trip_counter"):
    '''ermittelt die letzte Fahrt auf der DB'''
    try:
        return pd.read_sql_query(f'SELECT {tripid} FROM {tabellenname} ORDER BY {tripid} DESC limit 1;',con=engine)
    except:
        print(f'lasttrip_fehler \n {tabellenname} \n {tripid}')
        return 0
def tripermitteln():
        '''gibt des zu verarbeitenden Trip zurück - Übersicht '''
        start= int()
        try:
            counteru = lasttrip(uebersichts_tabelle,"trip_nummer")
            start = counteru.at[0,'trip_nummer']+1 #wert um 1 erhoehen

            counterc =lasttrip(raw_data_tabelle)
            ziel = counterc.at[0,'trip_counter']
            if ziel == start:
                print("alles hochgeladen")
                return -1
            else:
                return int(start)
        except:
            
            print("Fehler")
            return 0

def trip_handler(prozessanzahl):
    '''Verwaltet die Trips, jeder Prozess bekommt ein trip- callback fehlt'''
    global todo_trips
    
    wert= tripermitteln()
    if wert== -1:
        exit()
    for i in range(prozessanzahl):
        wert= wert+1
        todo_trips.append(wert)

    fertige=0
    while True:
        
        i=0
        for i in range(prozessanzahl):
            
            if todo_trips[i]=="weiter":
                wert= wert+1
                todo_trips[i]= wert
                print(todo_trips)
           

def trips(move=True):
    '''lädt die txt dateien auf die DB'''
    global path
    global engine
    
    fertig = int()

    if login_db == True:
        print("start")        
        menge_trips =0
        for file in os.listdir(path):
            if fnmatch.fnmatch(file,'[Trip_]*.txt'):
                menge_trips = int(menge_trips) +1
            update_gesamtanzeige(menge_trips, "max")    


        for file in os.listdir(path):#jede Datei im Ordner anschauen
                 
            if fnmatch.fnmatch(file,'[Trip]*.txt'):#wenn es eine Trip Datei ist   
                wertedertxtDatei = pd.read_csv(path+file, sep='\t')#einlesen der Text datei
                zahl = wertedertxtDatei.shape[0]#Länge der Datei bestimmen - zeilenanzahl für Trip_counter
                dupli = False
                try:
                    #verhindert das doppelte Hochladen von txt Dateien
                    duplikatsuche = pd.read_sql_query('SELECT Date, Time, trip_counter from fast_log1 group by trip_counter;',con=engine)
                    
                    
                    for c in range(int(duplikatsuche.shape[0])):
                        if duplikatsuche['Date'][c] == wertedertxtDatei['Date'][0] and duplikatsuche['Time'][c] == wertedertxtDatei['Time'][0]:
                            print("doppelte Datei gefunden")

                            if not(os.path.isdir(path+'fehler/')):
                                
                                print("kein Ordner vorhanden - Ordner wird erstellt")
                                os.makedirs(path+'fehler/')
                            shutil.move(path+file, path+'fehler/')
                            dupli = True
                            break 
                            
                            

                except Exception as e:
                    print(e)
                    #kann beim ersten starten ausgelöst werden
                    print("Fehler bei der Diplikatsuche"+ file)
                    #continue

                if(dupli):
                    fertig = fertig+1
                    update_gesamtanzeige(fertig)
                    continue
           
                try:#normalbetrieb
                    counter = pd.read_sql_query('SELECT trip_counter FROM fast_log1 ORDER BY fast_log1.trip_counter DESC limit 1;',con=engine)#letzten Trip-counter aus der DB holen
                    counter.at[0,'trip_counter'] = int(counter.at[0,'trip_counter']) +1 #wert um 1 erhöhen
                except Exception as e:
                    #print(e)
                    data = {'trip_counter':[0]} 
                    counter = pd.DataFrame(data) 

                if(zahl >= 10 and wertedertxtDatei['speed_obd'].max() >=10):
                    #wenn die Fahrt weniger als zirka 10 sekunden ging und man nciht schneller als 10km/h fuhr
                    pass


                DBcounter = counter#datenframe 1 definierne
                DBcounter2 = counter #datenframe2 definieren
                
                    
                
                for i in range(0, zahl): #jede Zeile in der Text Datei
                    DBcounter = DBcounter.append(DBcounter2, ignore_index = True)#anhängen des tripcounter an das hauptdatenframe
                    update_prozessanzeige(i) 
                    
                new = wertedertxtDatei.join(DBcounter)#tripcounter plus werte
                new.to_sql(raw_data_tabelle, con=engine, if_exists='append', index='counter')
            
                
                if (move == True):
                    if not(os.path.isdir(path+"Archiv/")):
                            print("kein Ordner vorhanden - Ordner wird erstellt")
                            os.makedirs(path+"Archiv/")      
                    shutil.move(path+file, path+'Archiv/')#verschiebt die bearbeitete Datei ins archiv
                #Werte zurücksetzen
                del counter  
                del DBcounter
                del DBcounter2
                fertig = fertig+1
                update_gesamtanzeige(fertig)
        update_gesamtanzeige(0)
        update_prozessanzeige(0)
    else:
        print("nicht angemeldet")    
    print("ENDE")
      
def dataframe_difference(df1, df2, which=None):
        """Find rows which are different between two DataFrames."""
        comparison_df = df1.merge(df2,
                                  indicator=True,
                                  how='outer')
        if which is None:
            diff_df = comparison_df[comparison_df['_merge'] != 'both']
        else:
            diff_df = comparison_df[comparison_df['_merge'] == which]
        #diff_df.to_csv('data/diff.csv')
        return diff_df

def sprit(sicherheitsabfrage ="Y"):#parameter sprit
        """Läd die Tankdaten ein, Datei mit dem Namen 1012177_fuelings.csv sollte im Root liegen"""
        global uebersichts_tabelle
        try:
            df1 =pd.read_csv("1012177_fuelings.csv", sep=';')#einlesen von der CSV datei
            try:#Verssucht Werte aus der DB zu bekommen und zu vergleichen
                df2 = pd.read_sql_table('spritkosten',
                                con=engine,
                                index_col='id')
                diff_df = dataframe_difference(df2, df1)
            
            except:#sollte z.b. keine Werte vorhanden sein oder es andere Fehler geben, Nutzeraufforderung
                sicherheitsabfrage = input("FehLER beim lesen, weitermachen ohne vorheriges Einladen Y/n")
                if sicherheitsabfrage == "Y":
                    print("Fehler gefunden")
                    diff_df=df1
            
                #wenn Nutzer nciht zustimmt - Abbruch    
                else:
                    exit()
        
            #Upload uf die DB 
            diff_df.to_sql(uebersichts_tabelle,
                con=engine,
                index=True,
                index_label='id',
                if_exists='append')
            print("fertig")
        except:
            print ("Keine Datei gefunden")

def uebersicht(theard_nr):
    print("start")
    '''generiert eine Übersicht, tripsweise'''
    global todo_trips
    print(todo_trips)

    while not(isinstance(todo_trips[theard_nr] , int)):
        time.sleep(0.1)
    tripnummer= todo_trips[theard_nr]
   
    #progressBarbuilder_uebersicht(theard_nr)
    query = f"""
    SELECT * FROM {raw_data_tabelle}
    WHERE trip_counter = {tripnummer} ORDER BY Date asc; """
    trip_auswertung3_0 = pd.read_sql_query(query, engine)
    zeilenanzahl = trip_auswertung3_0.shape[0]
   
    if(zeilenanzahl <= 20):
        todo_trips[theard_nr]= "weiter"
        print(f'keine Werte/ zu wenig gefunden für Trip {tripnummer}')
        if (zeilenanzahl == 0):
            todo_trips[theard_nr]= "fertig"
            exit()
        else:
            time.sleep(1)
            uebersicht(theard_nr)    
    df4 = pd.DataFrame(columns=['soc'])
 
    x = 0          
    for x in range(0, zeilenanzahl): #alle 0er aus dem Datensatz hauen, die Akkuzelle kann nie 0 % haben
        if trip_auswertung3_0.at[x,'soc'] != 0:
            df4 = df4.append( {'soc': float(trip_auswertung3_0.at[x,'soc'])}, ignore_index=True)
    
    C_soc_durchschnittlich = trip_auswertung3_0['soc'].mean()

    C_soc_start = df4.at[0, "soc"]

    C_soc_min =df4['soc'].min()

    C_soc_max = trip_auswertung3_0['soc'].max()

    C_soc_ende = trip_auswertung3_0['soc'][zeilenanzahl-1]

  
    verbauch_durchschnitt= float(trip_auswertung3_0['tripfuel'][zeilenanzahl-1])/10/float(trip_auswertung3_0['trip_dist'][zeilenanzahl-1])#verbrauch km/l
    ev_anteil = float(trip_auswertung3_0['trip_dist'][zeilenanzahl-1])+ float(trip_auswertung3_0['trip_ev_dist'][zeilenanzahl-1])/2# Anteil der elektrisch gefahren wurde
    

    aktueller_wert = C_soc_start
    plus = 0
    minus = 0

    for i in range(zeilenanzahl-1):
    #berechung wie die Akkuladung entwickelt hat
        if int(trip_auswertung3_0['soc'][i]) == aktueller_wert:
            pass
        elif int(trip_auswertung3_0['soc'][i]) <= aktueller_wert:
            plus = plus +1
            aktueller_wert = int(trip_auswertung3_0['soc'][i])
            
        elif int(trip_auswertung3_0['soc'][i]) >= aktueller_wert:    
            minus = minus +1
            aktueller_wert = int(trip_auswertung3_0['soc'][i])
        else:
            print("komischer Wert")
        aktueller_wert = int(trip_auswertung3_0['soc'][i])
  

    #der eigentliche Datensatz    
    uebersichtswerte ={'trip_nummer' : trip_auswertung3_0['trip_counter'][1],
                        'tag': pd.Timestamp(trip_auswertung3_0['Date'][0]),
                        'uhrzeit_Beginns' : trip_auswertung3_0['Time'][0], 
                        'uhrzeit_Ende': trip_auswertung3_0['Time'][zeilenanzahl-1],
                        'kmstand_start' : trip_auswertung3_0['odo'][0],
                        'trip_laenge': trip_auswertung3_0['trip_dist'][zeilenanzahl-1],
                        'trip_laengeev': trip_auswertung3_0['trip_ev_dist'][zeilenanzahl-1],
                        'fahrzeit': trip_auswertung3_0['trip_nbs'][zeilenanzahl-1],
                        'fahrzeit_ev': [trip_auswertung3_0['trip_ev_nbs'][zeilenanzahl-1]],
                        'fahrzeit_bewegung':  trip_auswertung3_0['trip_mov_nbs'][zeilenanzahl-1],
                        'spritverbrauch': [trip_auswertung3_0['tripfuel'][zeilenanzahl-1]],
                        'max_aussentemperatur':[trip_auswertung3_0['ambient_temp'].max()], 
                        'aussentemperatur_durchschnitt' : [trip_auswertung3_0['ambient_temp'].mean()],
                        'soc_durchschnitt' : [C_soc_durchschnittlich],
                        'soc_minimum':[C_soc_min],
                        'soc_maximal':[C_soc_max],
                        'soc_start':[C_soc_start],
                        'soc_ende':[C_soc_ende],
                        'soc_plus':[plus],
                        'soc_minus':[minus],
                        'verbauch_durchschnitt': [int(verbauch_durchschnitt)],
                        'ev_anteil':[int(ev_anteil)],
                        'geschwindichkeit_durchschnitt':[trip_auswertung3_0['speed_obd'].mean()],
                        'geschwindichkeit_maximal':[trip_auswertung3_0['speed_obd'].max()],
                        'soc_veraenderung': [int(C_soc_start) - int(C_soc_ende) ]
                        
                        } 
   

    del C_soc_ende
    del C_soc_max
    del C_soc_min
    del C_soc_start
        
        
    uebersichtges = pd.DataFrame(data=uebersichtswerte)
    
    del trip_auswertung3_0
    del uebersichtswerte
    
    sperre.acquire()
    uebersichtges.to_sql(uebersichts_tabelle,
                con=engine,
                index=True,
                index_label='id',
                if_exists='append')
    sperre.release()  
    del uebersichtges

    print ("fertig"+ str(tripnummer))
    todo_trips[theard_nr]="weiter"
    time.sleep(0.5)    
    uebersicht(theard_nr=theard_nr)    

def Programmauswahl(programm):
    '''startet die Programme und übergibt ihnen gegebenfalls die Werte'''
    global prozess
    prozesse = []
    if programm =="trips":
        p1= threading.Thread(target=trips, args=(True,))
        p1.start()
    elif programm == "sprit":
        p2= threading.Thread(target=sprit, args=(False,))
        p2.start()
    elif programm == "ueberischt":
        zahlx= int(prozess.get())
        p3= threading.Thread(target=trip_handler, args=(zahlx,))
        p3.start()
        time.sleep(0.5)
        for i in range (int(prozess.get())):
            threading.Thread()
            prozesse.append(threading.Thread(target=uebersicht, args=(i,)))
            prozesse[i].start()
            time.sleep(1)

    else:
        print("unbekanntes Programm")       
        
plattform_check()# überprüfung des betriebsystem

#Grafische Anzeige
root = Tk()
root.title('HA- Tool')
root.geometry("420x350")

gesFrame = LabelFrame()
gesFrame.grid(column=0,row=1)

#grafikoberfläche
buttonFrame = LabelFrame(gesFrame,text="Programmauswahl")
buttonFrame.grid(column=0,row=1)


#Knopf der Alle Trips einläd
button1 = ttk.Button(buttonFrame, text="Trips",command= lambda pragramm="trips" :Programmauswahl(pragramm))
button1.grid(column = 0, row = 2,  padx=5, pady=5)

#Läd die Sprittabelle ein
button1 = ttk.Button(buttonFrame, text="Sprit ",command= lambda pragramm="sprit" :Programmauswahl(pragramm))
button1.grid(column = 1, row = 2, padx=5, pady=5)

#Übersicht wird erstellt - CPU Anzahl bearbeiten und Multicore
button1 = ttk.Button( buttonFrame, text="Übersicht ",command=lambda pragramm="ueberischt" :Programmauswahl(pragramm))
button1.grid(column = 3, row = 2, padx=5, pady=5,)

#Prozess auswahl
prozess = StringVar(root)

choices = { 1,2,3,4,6,8,12,16}
prozess.set(1) # set the default option

prozessanzahl = OptionMenu(buttonFrame, prozess, *choices)
prozessanzahl.grid(row = 2, column =4)



progesFrame = LabelFrame(gesFrame,text="Gesamtfortschritt")
progesFrame.grid(column=0,row=3)

#Prozessor die den gesammten Fortschritt anzeigen soll
progressBarges = ttk.Progressbar(progesFrame, orient="horizontal", length=400)
progressBarges.grid(column = 1, row = 4, columnspan=4, padx=5, pady=5)
progressBarges['value']=0

#Prozess 1- zeigt den ungefähren Forschritt an beim erstellen der Ueberischt
progressBarpro = ttk.Progressbar(progesFrame, orient="horizontal", length=400)
progressBarpro.grid(column = 1, row = 5, padx=5, pady=5)
progressBarpro['value']=0


loginFrame = LabelFrame(gesFrame,text="Login für DB")
loginFrame.grid(column=0,row=6)

#Beschriftungen
Label(loginFrame, text="Benutzername*").grid(row=7)
Label(loginFrame, text="Passwort*").grid(row=8)
Label(loginFrame, text="Schema").grid(row=9)
Label(loginFrame, text="Port").grid(row=10)
Label(loginFrame, text="IP Adresse").grid(row=11)


#logindaten
User = StringVar()
Pass = StringVar()
DB_schema = StringVar()
anschluss = StringVar()
ip = StringVar()
loginsuccess = StringVar()
loginsuccess.set("NICHT ANGEMELDET")

ip.set("127.0.0.1")
DB_schema.set("car")
anschluss.set("3306")

#Eingaben
e1 = Entry(loginFrame,textvariable=User)
e2 = Entry(loginFrame, show="*", textvariable=Pass)
e3 = Entry(loginFrame, textvariable=DB_schema)
e4 = Entry(loginFrame, textvariable=anschluss)
e5 = Entry(loginFrame, textvariable=ip)

button4 = ttk.Button( loginFrame, text="LOGIN",command= lambda: login_value(create="yes"))
button4.grid(column = 1, row = 12, padx=5, pady=5,)

label_loginsuccess= Label(loginFrame, bg = "red",textvariable=loginsuccess)
label_loginsuccess.grid(row=13)
e1.grid(row=7, column=1)
e2.grid(row=8, column=1)
e3.grid(row=9, column=1)
e4.grid(row=10, column=1)
e5.grid(row=11, column=1)




def update_gesamtanzeige(value, action = "value"):
    '''Update der Gesamtanzeige'''
    if action == "value":    
        progressBarges['value']= int(value)
        progressBarges.update()
    else:
        progressBarges['maximum']= int(value)
        progressBarges.update()    
        
def update_prozessanzeige(value, action = "value"):
    '''Update des einzelnen Prozess'''
    if action == "value":
        progressBarpro['value']=int(value)
        progressBarpro.update()
    else:
        progressBarpro['maximum']=int(value)
        progressBarpro.update()  

root.mainloop()