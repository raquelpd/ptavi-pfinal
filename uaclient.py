#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Programa cliente que abre un socket a un servidor
"""

import socket
import sys
import xml.etree.ElementTree
import time

# Cliente UDP simple.

# Dirección IP del servidor.
if len(sys.argv) !=4:
    sys.exit('Usage: Python clientpy method receiver@IP:SIPport')
#$ python uaclient.py config metodo opcion   !!

METHOD = sys.argv[2]
Fich = sys.argv[1]
Option = sys.argv[3]

e = xml.etree.ElementTree.parse(Fich).getroot()

#Datos ua.xml
username = e[0].attrib["username"]
passwd = e[0].attrib["passwd"]
IPserver = e[1].attrib["ip"]
PORTserver = int(e[1].attrib["port"])
IPproxy =  e[3].attrib["ip"]
PORTproxy = int(e[3].attrib["port"])
PORTrtp = int(e[2].attrib["port"])
LOGpath = e[4].attrib["path"]
AUDIOpath = e[5].attrib["path"]

# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
my_socket.connect((IPproxy, PORTproxy))

#creamos log.txt
log = open('Log.txt', 'w')

if METHOD not in ["REGISTER", "INVITE", "BYE"]:
	sys.exit('Invalid Method')
else: 
	if METHOD == "REGISTER":
		LINE = METHOD + " sip:" + username + "SIP/2.0\r\n" + "Expires: " + Option
		print("Enviando: " + LINE)

		Hora = time.time()
		Evento = "send To" + IPproxy + ":" + str(PORTproxy) + ":" + LINE
		Log = open('Log.txt', 'a')
		Log.write(str(Hora) + " " + Evento)

		my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
		try:
	   		data = my_socket.recv(1024)
		except ConnectionRefusedError:
	    		sys.exit('Conection Refused')


	elif METHOD == "INVITE":
		print("Sin terminar")
	elif METHOD == "bye": 
		print("bye")


	print('Recibido --' + '\r\n', data.decode('utf-8'))
	if METHOD == 'INVITE':
	    I1 = data.decode('utf-8').split()[1]
	    I2 = data.decode('utf-8').split()[4]
	    I3 = data.decode('utf8').split()[7]
	    if I1 == '100' and I2 == '180' and I3 == '200':
	        Line = 'ACK ' + 'sip:' + LOGIN + IP + ' SIP/2.0\r\n'
	        print('Sending: ' + Line)
	        my_socket.send(bytes(Line, 'utf-8') + b'\r\n')
	        data = my_socket.recv(1024)
	elif METHOD == 'BYE':
	    print("Terminando socket...")
	    # Cerramos todo
	    my_socket.close()
	    print("Fin.")




