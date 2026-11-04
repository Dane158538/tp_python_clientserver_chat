import socket #utilisé pour communiquer entre ordinateurs
import sys  #utilisé pour sortir du programme
import time #utilisé pour faire des pauses
from clientthread import ClientListener #importation de la classe ClientListener du fichier clientthread.py

class Server():
    
    
    #serveur qui écoute sur le port donné et qui accepte les connexions des clients
    def __init__(self, port):
        self.listener= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.bind(('', port))
        self.listener.listen(1)
        print("Listening on port", port)
        self.clients_sockets= []

    #fonction qui écoute les clients et crée un thread pour chaque client
    def run(self):
        while True:
            print("listening new customers")
            try:
                (client_socket, client_adress) = self.listener.accept()
            except socket.error:
                sys.exit("Cannot connect clients")
            self.clients_sockets.append(client_socket)
            print("Start the thread for client:", client_adress)
            client_thread= ClientListener(self, client_socket, client_adress)
            client_thread.start()
            time.sleep(0.1)

    #Retire un client de la liste lorsqu'il se déconnecte
    def remove_socket(self, socket):
        self.clients_sockets.remove(socket)

    #Affiche le message reçu et l'envoie à tous les clients connectés
    def echo(self, data):
        print("echoing:", data)
        for sock in self.clients_sockets:
            try:
                sock.sendall(data.encode("UTF-8"))
            except socket.error:
                print("Cannot send the message")


    # Démarre le serveur pour accepter les connexions
if __name__ == "__main__":
    server= Server(59001)
    server.run()
