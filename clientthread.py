from socket import socket # utilisé pour communiquer entre ordinateurs
import threading # utilisé pour créer des threads
import re # utilisé pour les expressions régulières
import time # utilisé pour faire des pauses

# class qui permet de gérer chaque client dans un thread séparé
class ClientListener(threading.Thread): 

    # initialise le thread avec le serveur le socket et l'adresse du client
    def __init__(self, server, socket, address):
        super(ClientListener, self).__init__()
        self.server= server
        self.socket= socket
        self.address= address
        self.listening= True
        self.username= "No username"

    # écoute les messages envoyés par le client
    def run(self):
        while self.listening:
            data= ""
            try:
                data = self.socket.recv(1024).decode('UTF-8')
            except socket.error:
                print("Unable to receive data")
            self.handle_msg(data)
            time.sleep(0.1)
        print("Ending client thread for", self.address)
 
    # déconnecte le client et prévient les autres clients
    def quit(self):
        self.listening = False
        self.socket.close()
        self.server.remove_socket(self.socket)
        self.server.echo("{0} has quit\n".format(self.username))

    # gère les messages reçus selon leur contenu
    def handle_msg(self, data):
        print(self.address, "sent :", data)
        username_result = re.search('^USERNAME (.*)$', data) # vérifie si le client envoie un nom d'utilisateur
        
        # déconnecte le client s'il envoie quit ou un message vide sinon affiche l'envoie à tous les clients connectés
        if username_result:
            self.username = username_result.group(1)
            self.server.echo("{0} has joined.\n".format(self.username))
        elif data == "QUIT":
            self.quit()
        elif data == "":
            self.quit()
        else:
            self.server.echo(data)
