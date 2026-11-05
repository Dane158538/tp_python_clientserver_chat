import socket #utilisé pour communiquer entre ordinateurs
import sys  #utilisé pour sortir du programme
import threading
import time #utilisé pour faire des pauses
from clientthread import ClientListener #importation de la classe ClientListener du fichier clientthread.py
import datetime

class Server():

    #serveur qui écoute sur le port donné et qui accepte les connexions des clients
    def __init__(self, port):
        self.log_file = f"server_{port}.log"
        with open(self.log_file, "w") as f:
            f.write(f"--- Serveur demarre sur le port {port} ---\n")
            # Initialise ou réinitialise le fichier de log du serveur

        self.listener= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.bind(('', port))
        self.listener.listen(1)
        self.log(f"Listening on port {port}")
        self.clients_sockets= []
        self.lock= threading.Lock()  # Lock pour sécuriser l'accès/modification de clients_sockets

    def log(self, message):
        """Écrit un message avec date/heure dans le fichier de log du serveur"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a") as f:
            f.write(f"[{timestamp}] {message}\n")

    #fonction qui écoute les clients et crée un thread pour chaque client
    def run(self):
        while True:
            self.log("listening new customers")
            try:
                (client_socket, client_adress) = self.listener.accept()
            except socket.error:
                sys.exit("Cannot connect clients")
            with self.lock: 
                self.clients_sockets.append(client_socket)
                # accès par un thread à la fois
            self.log(f"Start the thread for client: {client_adress}")
            client_thread= ClientListener(self, client_socket, client_adress)
            client_thread.start()
            time.sleep(0.1)

    #Retire un client de la liste lorsqu'il se déconnecte
    def remove_socket(self, socket):
        with self.lock:
            self.clients_sockets.remove(socket)
            # accès par un thread à la fois

    #Affiche le message reçu et l'envoie à tous les clients connectés
    def echo(self, data):
        self.log(f"echoing: {data}")
        with self.lock: # accès par un thread à la fois
            for sock in self.clients_sockets:
                try:
                    sock.sendall(data.encode("UTF-8"))
                except socket.error:
                    self.log("Cannot send the message")
                    print("Cannot send the message")


    # Démarre le serveur pour accepter les connexions
if __name__ == "__main__":
    server= Server(59001)
    server.run()
