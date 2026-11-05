import os
import threading
import socket
import time
import re
import json

import inputValidate
import server

server_list_json = "serverslist.json"

class Client():

    def __init__(self, username, server, port):
        """Initialise le client avec l'username, l'adresse du serveur et le port du serveur"""
        self.socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM) #créer un socket TCP
        try:
            self.socket.connect((server, port)) #se connecte au serveur avec l'adresse et le port fourni
        except (socket.error, ConnectionRefusedError):
            raise ConnectionError("Unable to connect to the server. Please check the server address and port.")
        self.username= username
        self.send("USERNAME {0}".format(username)) #envoit l'username au serveur
        self.listening= True


    def listener(self):
        """Écoute les messages du serveur et les affiche"""
        while self.listening:
            data= ""
            try:
                data= self.socket.recv(1024).decode('UTF-8') #peut recevoir un message jusqu'à 1024 octets et le décode en UTF-8
            except socket.error:
                # eviter d'afficher l'erreur quand l'utilisateur 'QUIT'
                if self.listening:
                    print("Unable to receive data")
                    self.tidy_up() 
                    os._exit(0) #ferme le programme (pas que le thread) si le serveur est hors ligne
                break

            self.handle_msg(data) #envoit les données reçues à la fonction handle_msg
            time.sleep(0.1)


    def listen(self):
        """Créer un thread pour écouter les messages du serveur sans bloquer le thread principal"""
        self.listen_thread = threading.Thread(target=self.listener) #créer le thread écoutant la fonction listener()
        self.listen_thread.daemon = True #arrêt automatique du thread
        self.listen_thread.start()

    def send(self, message):
        """Envoyer un message au serveur"""
        try:
            if message == "QUIT":
                self.socket.sendall(message.encode("UTF-8"))
                self.tidy_up()
                return
            username_result = re.search('^USERNAME (.*)$', message)
            if not username_result:
                message= "{0}: {1}".format(self.username, message)
                #si le message n'a pas d'username, on ajoute l'username au début du message
            self.socket.sendall(message.encode("UTF-8"))
            #envoit le message encodé en UTF-8 au serveur
        except (socket.error, ConnectionResetError):
            print("unable to send message, server might be offline.")
            self.tidy_up()


    def tidy_up(self):
        """Ferme le socket et arrête le thread"""
        self.listening = False #la boucle de listener() s'arrête
        self.socket.close()

    def handle_msg(self, data):
        """Gère les messages reçus du serveur"""
        if data=="QUIT":
            self.tidy_up()
            #si le serveur envoit 'QUIT', on appelle la fonction tidy_up() pour fermer le socket et arrêter le thread
        elif data=="":
            self.tidy_up()
            #si le serveur ferme la connexion, on appelle à nouveau la fonction tidy_up()
        else:
            if hasattr(self, "afficher_message"):
                self.afficher_message(data)
            else:
                print(data)

def run_server_target(port):
    """Fonction exécutée par le thread pour créer et lancer le serveur"""
    srv = server.Server(port)
    srv.run()

def initServerThread(port):
    """Initialise un serveur dans un thread séparé."""
    thread = threading.Thread(target=run_server_target, args=(port,))
    thread.daemon = True
    thread.start()

def add_server():
    port = 59001
    existing_ports = [srv["port"] for srv in server_list]
    while port in existing_ports:
        port += 1
    #choisi un port disponible pour le serveur
    initServerThread(port)
    with open(server_list_json, "w") as f:
            server_list.append({"port": port, "count": 0})
            json.dump(server_list, f) #rajoute le port du serveur à la liste des serveurs disponibles
    print(f"Server is running on port {port}.")
    return port

def change_user_count(port, isDecrement = False):
    """trouve le serveur concerné et enlève ou ajoute l'user du count"""
    for server in server_list:
        if server.get("port") == port:
            current_count = server.get("count")
            if isDecrement:
                server["count"] = max(0, current_count-1)
            else:
                server["count"] = current_count +1
            break
    with open(server_list_json, "w") as f:
        json.dump(server_list, f)

def new_server_connection():
    print("Starting a new server...")
    port= add_server()
    username= inputValidate.validateUsername()
    return port, username

if __name__ == "__main__":
    server_list = []
    with open(server_list_json) as f:
        server_list = json.load(f)
    if server_list != []:
            join = input("Do you want to join an existing server? (y/n): ")
            if join.lower() == "y":
                print("Servers available:")
                for srv in server_list:
                    print(" port: ", srv["port"],", connectés: ", srv["count"], " ." )
                port= inputValidate.validatePort()
                username= inputValidate.validateUsername()
            else:
                port, username = new_server_connection()
    else:
        port, username = new_server_connection()
    try:
        client= Client(username, "127.0.0.1", port)
        change_user_count(port, False)
    except ConnectionError as e:
        print(e)
        os._exit(1)

    client.listen() #écoute les messages du serveur
    message= ""
    try:
        while message!="QUIT":
            message= input()
            client.send(message)
            #si l'utilisateur saisit 'QUIT', le programme se termine et le socket est fermé
            #sinon, le message est envoyé au serveur
    finally: #prend en compte le Ctrl+C sur le terminal
        change_user_count(port, True)

        with open(server_list_json) as f:
                server_list = json.load(f)

        for i in range(len(server_list)):
            if server_list[i].get('port') == port and server_list[i].get("count") == 0:
                del server_list[i]
                break
        #supprime le serveur de la liste seulement si tous les users sont déconnectés

        with open(server_list_json, "w") as f:
            json.dump(server_list, f)
            
        os._exit(0)
