import sqlite3 #Biblioteca para manejo de Bases de Datos
import json    #Biblioteca para manipulacion de archivos json
import csv	   #Biblioteca para manipulacion de archivos CSV
import smtplib #Bibliotecas para envio de correos
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

########### FUNCIONES ################
###Envio de correos
def enviarCorreo(mensaje,mail):
    print ("ENVIANDO EMAIL PARA REVALIDA DE CLASIFICACION")
    print(mail)
    user="nicochallengeml@gmail.com"
    password="challengeml"
#Para las cabeceras del mail
    remitente="Nico Ricci Challenge <nicochallengeml@gmail.com>"
    destinatario=mail
    asunto="Clasificacion de activos - Revalida 2019"
    msj=str(mensaje)
#Host y puerto SMTP de gmail
    gmail=smtplib.SMTP('smtp.gmail.com',587)
#Protocolo de cifrado de datos utilizados por Gmail
    gmail.starttls()
#Credenciales
    gmail.login(user,password)
#Para que no muestre la deputacion de la operacion de envio (0=false)
    gmail.set_debuglevel(0)
    header=MIMEMultipart()
    header['Subject']=asunto
    header['From']=remitente
    header['To']=destinatario
    msj=MIMEText(mensaje, 'html') #Content-type:text/html
    header.attach(msj) 
#Enviar email
    gmail.sendmail(remitente,destinatario,header.as_string())
#Cerrar la conexion SMTP
    gmail.quit()

###Creacion de Bases de Datos
def createDB():
	miConexion=sqlite3.connect("DB")
	miCursor=miConexion.cursor()
	miCursor.execute("""
		CREATE TABLE IF NOT EXISTS BASES (
		ID_BASE INTEGER PRIMARY KEY AUTOINCREMENT,
		NOMBRE_BASE VARCHAR(30),
		EMAILOWNER VARCHAR(50),
		EMAILMANAGER VARCHAR(50),
		CONFIDENCIALIDAD VARCHAR(20),
		INTEGRIDAD VARCHAR(20),
		DISPONIBILIDAD VARCHAR(20)
		)
		""")
	miConexion.close()

###Insercion de valores en la Base de datos
def insertarBD(dn_name,ownermail,managermail,confidencialidad,integridad,disponibilidad):
	miConexion=sqlite3.connect("DB")
	miCursor=miConexion.cursor()
	miCursor.execute("""INSERT INTO BASES (NOMBRE_BASE,EMAILOWNER,EMAILMANAGER,CONFIDENCIALIDAD,INTEGRIDAD,DISPONIBILIDAD) VALUES (?,?,?,?,?,?)""",[dn_name,ownermail,managermail,confidencialidad,integridad,disponibilidad])
	miConexion.commit()
	miConexion.close()


#### IMPORTO ARCHIVO .CSV Y LO AGREGO A UNA LISTA
def importarArchivos():
	global listaCSV
	listaCSV=[]
	with open('user_manager.csv', 'r') as archivo:
		reader = csv.reader(archivo)
		for fila in reader:
			listaCSV.append(fila)

### IMPORTO ARCHIVO .JSON
	with open('dblist.json') as f:
		data=json.load(f)       

### RECORRO ARCHIVO JSON, SI NO EXISTE MAIL PARA OWNER: LO CREO.
### IMPRIMO VALORES NECESARIOS
def recorrerArchivosYcompletar():
    with open('dblist.json') as f:
            data=json.load(f)
	
    for database in data['db_list']:
        if 'email' not in database['owner']:
            database['owner']['email'] = ""
            with open('new_dblist.json', 'w') as f:
                json.dump(data, f)

### RECORRO LA LISTA CSV Y POR CADA FILA CHEQUEO SI EL OWNER ES IGUAL AL VALOR ACTUAL DEL DICCIONARIO
### SI ENCUENTRO MACH ENTONCES LLAMO A FUNCION INSERTAR EN BASE DE DATOS
def insertarBDyEnviarCorreo():
	with open('new_dblist.json') as f:
		data=json.load(f)
	for database in data['db_list']:
		for row in listaCSV:
			if row[1] == database['owner']['uid']:
				database['owner']['manager'] = row[3]
				insertarBD(database['dn_name'],database['owner']['email'],database['owner']['manager'],database['classification']['confidentiality'],database['classification']['integrity'],database['classification']['availability'])
				if database['classification']['confidentiality'] == 'high' or (database['classification']['integrity']=='high') or (database['classification']['availability']=='high') or database['classification']['confidentiality'] == '' or (database['classification']['integrity']=='') or (database['classification']['availability']==''): 
					mensaje="Buen dia, como manager del owner: "+database['owner']['name']+" de la base "+database['dn_name']+" se le solicita validar la siguiente clasificación--> CONFIDENCIALIDAD: "+database['classification']['confidentiality']+" INTEGRIDAD: "+database['classification']['integrity']+" DISPONIBILIDAD: "+database['classification']['availability']+". En caso de no estar clasificada, por favor enviar la informacion completa."
					str(mensaje)
					enviarCorreo(mensaje,database['owner']['manager'])
				with open('new_dblist.json', 'w') as f:
					json.dump(data, f)	

#### MAIN ######
createDB()
importarArchivos()
recorrerArchivosYcompletar()
insertarBDyEnviarCorreo()

	





