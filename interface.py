import tkinter as tk
from client import Client
import queue

client = None
fenetre = tk.Tk() # fenêtre principale

fenetre.title("Chat") # titre 
fenetre.geometry("500x400") # taille 
fenetre.configure(bg="#1e2430")
cadre_connexion = tk.Frame(fenetre, bg="#2b3444")
cadre_connexion.pack(pady=10)

# Pseudo
label_username = tk.Label(cadre_connexion, text="Pseudo :", bg="#2b3444", fg="white")
label_username.grid(row=0, column=0, padx=5, pady=5)

champ_username = tk.Entry(cadre_connexion, width=15)
champ_username.grid(row=1, column=0, padx=5)

# Adresse IP
label_server = tk.Label(cadre_connexion, text="Adresse IP :", bg="#2b3444", fg="white")
label_server.grid(row=0, column=1, padx=5, pady=5)

champ_server = tk.Entry(cadre_connexion, width=15)
champ_server.grid(row=1, column=1, padx=5)

# Port
label_port = tk.Label(cadre_connexion, text="Port :", bg="#2b3444", fg="white")
label_port.grid(row=0, column=2, padx=5, pady=5)

champ_port = tk.Entry(cadre_connexion, width=10)
champ_port.grid(row=1, column=2, padx=5)
messages = queue.Queue()

def afficher_messages():
    while not messages.empty():
        message = messages.get()
        zone_messages.insert(tk.END, message + "\n")

    fenetre.after(100, afficher_messages)

# fonction qui récupère les informations de l'utilisateur et les affiche
def connexion():
    global client
    username = champ_username.get()
    server = champ_server.get()
    port = champ_port.get()
    client = Client(username, server, int(port))
    client.afficher_message = messages.put
    client.listen()
    
# fonction qui envoie le message écrit par l'utilisateur 
def envoyer():
    message = champ_message.get()

    if message != "" and client is not None:
        client.send(message)
        champ_message.delete(0, tk.END)

# bouton de connexion 
bouton_connexion = tk.Button(
    cadre_connexion,
    text="Connexion",
    command=connexion
)

bouton_connexion.grid(row=2, column=0, columnspan=3, pady=10)

# Zone pour afficher les messages
zone_messages = tk.Text(fenetre, height=10, width=40, bg="#2b3444", fg="white")
zone_messages.pack(pady=10)

afficher_messages() 

champ_message = tk.Entry(fenetre, width=40, bg="#2b3444", fg="white")
champ_message.pack(pady=5)

bouton_envoyer = tk.Button(fenetre, text="Envoyer", command=envoyer, bg="#4a5568", fg="white")
bouton_envoyer.pack(pady=5)

champ_message.bind("<Return>", lambda event: envoyer())

fenetre.mainloop() # reste ouverte jusqu'à ce qu'on la ferme
