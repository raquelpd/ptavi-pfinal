#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""
import socket
import socketserver
import sys
import os.path
import os
import xml.etree.ElementTree
import random
import time
global passwords
import hashlib
import json


class EchoHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """
    client_list = []

    def register2json(self):

        json_file = open('registered.json', 'w')
        json.dump(self.client_list, json_file, indent='\t')

    def json2registered(self):

        try:
            with open('registered.json') as client_file:
                self.client_list = json.load(client_file)
        except:
            self.register2json()

    def handle(self):
        # Escribe dirección y puerto del cliente (de tupla client_address)
        IP = self.client_address[0]
        PORT = self.client_address[1]

        #creamos log.txt
        log = open(LOGpath, 'w')

        now = time.gmtime(time.time())
        Hora = time.strftime('%Y-%m-%d %H:%M:%S', now)
        Evento= 'Starting...\r\n'
        Log = open(LOGpath, 'a')
        Log.write(Hora + " " + Evento)

        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()

            if not line:
                break

            print("El cliente nos manda--\r\n " + line.decode('utf-8'))
            Instruction = line.decode('utf-8')
            LINE = Instruction.split('\r\n')
            METHOD = Instruction.split(' ')[0]
            Direction = Instruction.split(' ')[1].split(':')[1]
            nonce = random.randint(0, 999999999999999999999)
            client_list = []

            #Log
            Evento = 'Recived from ' + IP + ':' + str(PORT) + ': ' + LINE[0]
            now = time.gmtime(time.time())
            Hora = time.strftime('%Y-%m-%d %H:%M:%S', now)
            Log = open(LOGpath, 'a')
            Log.write(str(Hora) + " " + Evento)

            if METHOD == 'REGISTER':

                if LINE[2].split(' ')[0] != 'Authorization:' :
                    Line = "SIP/2.0 401 Unauthorized\r\nWWW Authenticate: Digest nonce=" + str(nonce) + '\r\n'
                    Evento = 'Sent to' + IP + ':' + str(PORT) + ': ' + Line[0]
                    now = time.gmtime(time.time())
                    Hora = time.strftime('%Y-%m-%d %H:%M:%S', now)
                    Log = open(LOGpath, 'a')
                    Log.write(str(Hora) + " " + Evento)
                    self.wfile.write(bytes(Line, "utf-8"))

                else:  #ya está autenticado
                    Direction = Instruction.split(' ')[1].split(':')[1]
                    passwords = open(DATABASEpasswd, 'r')
                    passwords = passwords.readlines()
                    #comprobamos la contraseña y a continuacion autenticamos el cliente
                    for User in passwords:
                        if Direction == User.split(' ')[0]:
                            passwords = User.split(' ')[1]
                            authenticate = hashlib.sha1()
                            authenticate.update(bytes(passwords, 'utf-8'))
                            authenticate.update(bytes(str(nonce), 'utf-8'))
                            authenticate = authenticate.hexdigest() 

                            Time_Exp = LINE[1].split(' ')[1] 
                            
                            Usuario = [Direction, {'IP': self.client_address[0],
                                        'port': Instruction.split(' ')[1].split(':')[2],
                                        'Time_Exp': str(Hora) + ' + ' + str(Time_Exp)}]      
                            #si el tiempo ha expirado borramos el cliente
                            if Time_Exp == 0:
                                for User in self.client_list:
                                    if User[0] == Direction:
                                        self.client_list.remove(Usuario) 
                            else:
                                for User in self.client_list:
                                    if User[0] == Direction:
                                        self.client_list.remove(Usuario)
                                self.client_list.append(Usuario)
                                print('Client succsfully registered\r\n')
                                Line = 'SIP/2.0 200 Ok'
                                self.wfile.write(bytes(Line, 'utf-8'))
                                #log
                                Evento = 'Sent to' + IP + ':' + str(PORT) + ': ' + Line
                                now = time.gmtime(time.time())
                                Hora = time.strftime('%Y-%m-%d %H:%M:%S', now)
                                Log = open(LOGpath, 'a')
                                Log.write(str(Hora) + " " + Evento)
                            #break 
                            self.register2json()
            elif METHOD == 'INVITE':
                for U in self.client_list:
                    if U[0] == Direction:
                        print('Usuario encontrado')
                        IPsrv= U[1]['IP']
                        PORTsrv = U[1]['port']
                        my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        my_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
                        my_socket.connect((IPsrv, int(PORTsrv)))
                        print('Reenviando: \r\n' + Instruction)
                        my_socket.send(bytes(Instruction, 'utf-8') + b'\r\n')
                        Stop = 'true'

                        #recibimos 100 trying, 180 ringing, 200 ok
                        data = my_socket.recv(int(PORTsrv))
                        data = data = data.decode('utf-8')
                        LINE = data.split('\r\n')
                        Cod1 = LINE[1].split(' ')[1].split(' ')[0]
                        Cod2 = LINE[3].split(' ')[1].split(' ')[0]
                        Cod3 = LINE[5].split(' ')[1].split(' ')[0]
                        if Cod1 == '100' : #and Cod2 == '180' : #ack
                            print('Recibido --\r\n ' + data )
                            self.wfile.write(bytes(data, "utf-8"))
                            print('reenviado')


                    if U[0] != Direction and Stop != 'true':
                        Line = "SIP/2.0 404 User Not Found\r\n\r\n"
                        print("Enviando: " + Line)
                        self.wfile.write(bytes(Line, "utf-8"))
                        #LOG
                        Evento = 'Sent to' + IP + ':' + str(PORT) + ': ' + Line
                        now = time.gmtime(time.time())
                        Hora = time.strftime('%Y-%m-%d %H:%M:%S', now)
                        Log = open(LOGpath, 'a')
                        Log.write(str(Hora) + " " + Evento)


            else:  #ACK
                for U in self.client_list:
                     if U[0] == Direction:
                        IPsrv= U[1]['IP']
                        PORTsrv = U[1]['port']
                        my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        my_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
                        my_socket.connect((IPsrv, int(PORTsrv)))
                        my_socket.send(bytes(Instruction, 'utf-8') + b'\r\n')
                #LOG
                Evento = 'Sent to' + IPsrv + ':' + str(PORTsrv) + ': ' + Instruction
                now = time.gmtime(time.time())
                Hora = time.strftime('%Y-%m-%d %H:%M:%S', now)
                Log = open(LOGpath, 'a')
                Log.write(str(Hora) + " " + Evento)




            # Si no hay más líneas salimos del bucle infinito
            if not line:
                break

if len(sys.argv) !=2:
        sys.exit('Usage: python proxy-registrar.py config')

Fich = sys.argv[1]

e = xml.etree.ElementTree.parse(Fich).getroot()

#Datos pr.xml
name = e[0].attrib["name"]
IPserver = e[0].attrib["ip"]
PORTserver = int(e[0].attrib["port"])
DATABASEpath =  e[1].attrib["path"]
DATABASEpasswd = e[1].attrib["passwdpath"]
LOGpath = e[2].attrib["path"]

if __name__ == "__main__":

    print('Server MiSrvidorBigBang listening at port 6001... \r\n')

    # Creamos servidor de eco y escuchamos
    serv = socketserver.UDPServer(('', PORTserver), EchoHandler)
    serv.serve_forever()
