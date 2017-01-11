#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

import socketserver
import sys
import os.path
import os
import xml.etree.ElementTree
import time


class EchoHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """
    def handle(self):
        # Escribe dirección y puerto del cliente (de tupla client_address)
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()
            print("El cliente nos manda \r\n" + line.decode('utf-8'))

            # Si no hay más líneas salimos del bucle infinito
            if not line:
                break

                Instruction = line.decode('utf-8')
                LINE = Instruction.split('\r\n')
                METHOD = Instruction.split(' ')[0]

                if METHOD == 'INVITE':
                    Direction = LINE[4].split('=')[1].split(' ')[0]
                    IPemisor = LINE[4].split('=')[1].split(' ')[1]
                    PORTemisor = LINE[7].split(' ')[1].split(' ')[0]

                    # Respuesta al cliente
                    header = 'Content-Type: application/sdp\r\n\r\n'
                    v = 'v=0\r\n'
                    o = 'o=' + username + ' ' + IPserver + '\r\n'
                    s = 's=misesion\r\n'
                    t = 't=0\r\n'
                    m = 'm=audio ' + str(PORTrtp) + ' RTP\r\n'

                    ctype = header + v + o + s + t + m
                    # log
                    Evento = 'Received from ' + IPemisor + ':' + str(PORTemisor) + ': ' + LINE[0] + '[...]\r\n'
                    now = time.gmtime(time.time())
                    Hora = time.strftime('%Y-%m-%d %H:%M:%S', now)
                    Log = open(LOGpath, 'a')
                    Log.write(str(Hora) + " " + Evento)

                    # 100trying, 180 ringing, 200 ok
                    Line = '\r\nSIP/2.0 100 Trying\r\n\r\n' + 'SIP/2.0 180 Ringing\r\n\r\n' + 'SIP/2.0 200 OK\r\n ' + ctype
                    self.wfile.write(bytes(Line, "utf-8"))
                    Evento = 'Sent to  ' + IPemisor + ':' + str(PORTemisor) + ': ' + LINE[0] + '[...]\r\n'
                    now = time.gmtime(time.time())
                    Hora = time.strftime('%Y-%m-%d %H:%M:%S', now)
                    Log = open(LOGpath, 'a')
                    Log.write(str(Hora) + " " + Evento)
                    break

                elif METHOD == 'BYE':
                    print('recibido bye')
                    # log
                    Evento = 'Received from ' + IPproxy + ':' + str(PORTproxy) + ': ' + LINE[0] + '[...]\r\n'
                    now = time.gmtime(time.time())
                    Hora = time.strftime('%Y-%m-%d %H:%M:%S', now)
                    Log = open(LOGpath, 'a')
                    Log.write(str(Hora) + " " + Evento)

                    Line = 'SIP/2.0 200 OK\r\n '
                    self.wfile.write(bytes(Line, "utf-8"))
                    # log
                    Evento = 'Send to  ' + IPproxy + ':' + str(PORTproxy) + ': ' + Line + '[...]\r\n'
                    now = time.gmtime(time.time())
                    Hora = time.strftime('%Y-%m-%d %H:%M:%S', now)
                    Log = open(LOGpath, 'a')
                    Log.write(str(Hora) + " " + Evento)

                else:  # ack

                    # log
                    Evento = 'Received from ' + IPproxy + ':' + str(PORTproxy) + ': ' + LINE[0] + '[...]\r\n'
                    now = time.gmtime(time.time())
                    Hora = time.strftime('%Y-%m-%d %H:%M:%S', now)
                    Log = open(LOGpath, 'a')
                    Log.write(str(Hora) + " " + Evento)
                    aEjecutar = 'mp32rtp -i ' + IPserver + ' -p ' + str(PORTrtp) + ' < ' + str(AUDIOpath)
                    print("Executing... ", aEjecutar)
                    os.system(aEjecutar)
                    print("Successfully sent")


if len(sys.argv) != 2:
    sys.exit('Usage: python uaserver.py config')

Fich = sys.argv[1]

if not os.path.exists(Fich):
    sys.exit('Usage: audio file oes not exists')

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


if __name__ == "__main__":

    print('listening...')

    # Creamos servidor de eco y escuchamos
    serv = socketserver.UDPServer(('', PORTserver), EchoHandler)
    print("Lanzando servidor UDP de eco...")
    serv.serve_forever()
