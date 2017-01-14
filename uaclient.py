#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Programa cliente que abre un socket a un servidor
"""

import socket
import sys
import xml.etree.ElementTree
import time
import random
import os


# Cliente UDP simple.

# Dirección IP del servidor.
if len(sys.argv) != 4:
    sys.exit('Usage: Python clientpy config method option')
# $ python uaclient.py config metodo opcion   !!

METHOD = sys.argv[2]
Fich = sys.argv[1]

e = xml.etree.ElementTree.parse(Fich).getroot()

# Datos ua.xml
username = e[0].attrib["username"]
passwd = e[0].attrib["passwd"]
IPserver = e[1].attrib["ip"]
PORTserver = int(e[1].attrib["port"])
IPproxy = e[3].attrib["ip"]
PORTproxy = int(e[3].attrib["port"])
PORTrtp = int(e[2].attrib["port"])
LOGpath = e[4].attrib["path"]
AUDIOpath = e[5].attrib["path"]

# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
my_socket.connect((IPproxy, PORTproxy))

# creamos log.txt


try:
    if METHOD not in ["REGISTER", "INVITE", "BYE"]:
        sys.exit('Invalid Method')
    else:
        Option = sys.argv[3]
        if METHOD == "REGISTER":
            LINE = METHOD + " sip:" + username + ":" + str(PORTserver) + " SIP/2.0\r\n" + "Expires: " + Option
            print("Enviando: " + LINE + '\r\n')

            # creamos log.txt
            log = open(LOGpath, 'w')
            now = time.gmtime(time.time())
            Hora = time.strftime('%Y-%m-%d %H:%M:%S', now)
            Evento = 'Starting...\r\n'
            Log = open(LOGpath, 'a')
            Log.write(Hora + " " + Evento)

            now = time.gmtime(time.time())
            Hora = time.strftime('%Y-%m-%d %H:%M:%S', now)
            Evento = "Sent To " + IPproxy + ":" + str(PORTproxy) + ": " + LINE.split('Expires: ')[0] + '[...]\r\n'
            Log = open(LOGpath, 'a')
            Log.write(Hora + " " + Evento)

            my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')

        elif METHOD == "INVITE":
            User = sys.argv[3]
            LINE = METHOD + " sip:" + User + ' SIP/2.0\r\n' + "Content-Type: application/sdp\r\n\r\n" + "v=0\r\n" + "o=" + username + " " + IPserver + "\r\ns=misesion\r\n" + "t=0\r\n" + "m=audio " + str(PORTrtp) + " RTP\r\n"
            my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
            # log
            now = time.gmtime(time.time())
            Hora = time.strftime('%Y-%m-%d %H:%M:%S', now)
            Evento = "Sent To " + IPproxy + ":" + str(PORTproxy) + ": " + LINE.split('\r\n')[0] + '[...]\r\n'
            Log = open(LOGpath, 'a')
            Log.write(Hora + " " + Evento)

        elif METHOD == "BYE":
            User = sys.argv[3]
            print('Terminando socket...')
            LINE = METHOD + " sip:" + User + " SIP/2.0"
            my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
            # log
            now = time.gmtime(time.time())
            Hora = time.strftime('%Y-%m-%d %H:%M:%S', now)
            Evento = "Sent To " + IPproxy + ":" + str(PORTproxy) + ": " + LINE.split('\r\n')[0] + '[...]\r\n'
            Log = open(LOGpath, 'a')
            Log.write(Hora + " " + Evento)
            # Cerramos todo
            my_socket.close()
            print("Fin.")

        data = my_socket.recv(int(PORTproxy))
        data = data.decode('utf-8')

        LINEA = data.split('\r\n')
        print('Recibido --' + '\r\n' + data)
        nonce = random.randint(0, 999999999999999999999)
        if METHOD == 'REGISTER':
            cod = LINEA[0].split(' ')[1].split(' ')[0]
            print(cod)

            now = time.gmtime(time.time())
            Hora = time.strftime('%Y-%m-%d %H:%M:%S', now)
            Evento = "Received from" + IPproxy + ":" + str(PORTproxy) + ": " + data.split('\r\n')[0] + '[...]\r\n'
            Log = open(LOGpath, 'a')
            Log.write(Hora + " " + Evento)
            if cod == '401':
                LINE = METHOD + " sip:" + username + ":" + str(PORTserver) + " SIP/2.0\r\n" + "Expires: " + Option + "\r\nAuthorization: Digest response= " + str(nonce)
                my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')

                now = time.gmtime(time.time())
                Hora = time.strftime('%Y-%m-%d %H:%M:%S', now)
                Evento = "Sent to " + IPproxy + ":" + str(PORTproxy) + ": " + LINE.split('\r\n')[0] + '[...]\r\n'
                Log = open(LOGpath, 'a')
                Log.write(Hora + " " + Evento)

                data = my_socket.recv(int(PORTproxy))
                data = data.decode('utf-8')
                LINEA = data.split('\r\n')
                cod = data.split(' ')[1].split(' ')[0]
                if cod != '401':
                    print('Recibido -- \r\n' + data)
                    # Log
                    now = time.gmtime(time.time())
                    Hora = time.strftime('%Y-%m-%d %H:%M:%S', now)
                    Evento = "Received From " + IPproxy + ":" + str(PORTproxy) + ": " + data.split('\r\n')[0] + '[...]\r\n'
                    Log = open(LOGpath, 'a')
                    Log.write(Hora + " " + Evento)

        elif METHOD == 'INVITE':
            cod = LINEA[1].split(' ')[1].split(' ')[0]
            if cod == '100':
                I2 = LINEA[3].split(' ')[1].split(' ')[0]
                I3 = LINEA[5].split(' ')[1].split(' ')[0]
                DirectionIP = LINEA[9].split('=')[1]
                # IP1 = LINEA[4].split(' ')[1]
                if cod == '100' and I2 == '180' and I3 == '200':
                    # ack
                    Line = 'ACK ' + 'sip:' + DirectionIP + ' SIP/2.0\r\n\r\n'
                    print('\r\nSending: ' + Line)
                    my_socket.send(bytes(Line, 'utf-8') + b'\r\n')
                    # log
                    now = time.gmtime(time.time())
                    Hora = time.strftime('%Y-%m-%d %H:%M:%S', now)
                    Evento = "Send to " + IPproxy + ":" + str(PORTproxy) + ": " + Line + '[...]\r\n'
                    Log = open(LOGpath, 'a')
                    Log.write(Hora + " " + Evento)
                    # Envio del audio
                    aEjecutar = './mp32rtp -i' + IPserver + ' -p' + str(PORTrtp) + ' <' + str(AUDIOpath)
                    os.system(aEjecutar)
                    print('Succesfully sent')
                    # log
                    now = time.gmtime(time.time())
                    Hora = time.strftime('%Y-%m-%d %H:%M:%S', now)
                    Evento = "Send to " + IPserver + ":" + str(IPserver) + ": " + data.split('\r\n')[0]
                    Log = open(LOGpath, 'a')
                    Log.write(Hora + " " + Evento)


except socket.error:
    now = time.gmtime(time.time())
    Hora = time.strftime('%Y-%m-%d %H:%M:%S', now)
    Evento = ' Error: No server listening at ' + IPproxy + ' port ' + str(PORTproxy)
    Log.write(Hora + " " + Evento)
