import os
import threading
import socket
import time
import re

import inputValidate

class Client():

    def __init__(self, username, server, port):
        """Initialise le client avec l'username, l'adresse du serveur et le port du serveur"""
        self.socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM) #créer un socket TCP
        self.socket.connect((server, port)) #se connecte au serveur avec l'adresse et le port fourni
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

if __name__ == "__main__":
    """Demande à l'utilisateur de saisir son nom d'utilisateur, le serveur et le port, puis crée un client avec les informations fournies et écoute les messages du serveur"""
    print("Please enter following information to connect to the server:")
    username= inputValidate.validateUsername()
    server= inputValidate.validateServer() 
    port= inputValidate.validatePort()
    
    client= Client(username, server, port)
    client.listen() #écoute les messages du serveur
    message= ""
    while message!="QUIT":
        message= input()
        client.send(message)
        #si l'utilisateur saisit 'QUIT', le programme se termine et le socket est fermé
        #sinon, le message est envoyé au serveur
