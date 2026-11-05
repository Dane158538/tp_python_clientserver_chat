import tkinter as tk
from client import Client
import queue
import ipaddress
from tkinter import messagebox

client = None
fenetre = tk.Tk() # fenêtre principale

fenetre.title("Chat") # titre 
fenetre.geometry("500x400") # taille 
fenetre.configure(bg="#1e2430")

# connexion
page_connexion = tk.Frame(fenetre, bg="#1e2430")
page_connexion.pack(fill="both", expand=True)

# chat
page_chat = tk.Frame(fenetre, bg="#1e2430")

cadre_connexion = tk.Frame(page_connexion, bg="#2b3444")
cadre_connexion.pack(pady=30)

# pseudo
label_username = tk.Label(cadre_connexion, text="Pseudo :", bg="#2b3444", fg="white")
label_username.grid(row=0, column=0, padx=5, pady=5)

champ_username = tk.Entry(cadre_connexion, width=15)
champ_username.grid(row=1, column=0, padx=5)

# adresse ip
label_server = tk.Label(cadre_connexion, text="Adresse IP :", bg="#2b3444", fg="white")
label_server.grid(row=0, column=1, padx=5, pady=5)

champ_server = tk.Entry(cadre_connexion, width=15)
champ_server.grid(row=1, column=1, padx=5)

# port
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
    if client is not None:
        messagebox.showwarning("Attention", "Tu es déjà connecté")
        return
    username = champ_username.get()
    server = champ_server.get()
    port = champ_port.get()
    if username.strip() == "":
        messagebox.showerror("Erreur", "Le pseudo ne peut pas être vide")
        return
    try:
        ipaddress.ip_address(server)
    except ValueError:
        messagebox.showerror("Erreur", "Adresse IP invalide")
        return
    try:
        port = int(port)
        if port < 1 or port > 65535:
            messagebox.showerror("Erreur", "Port invalide")
            return
    except ValueError:
        messagebox.showerror("Erreur", "Le port doit être un nombre")
        return
    try:
        client = Client(username, server, port)
        client.afficher_message = messages.put
        client.listen()
        info_client.config(text=f"Pseudo : {username} | IP : {server} | Port : {port}")
        page_connexion.pack_forget()
        page_chat.pack(fill="both", expand=True)
    except OSError:
        messagebox.showerror("Erreur", "Impossible de se connecter au serveur")
    
# fonction qui envoie le message écrit par l'utilisateur 
def envoyer():
    message = champ_message.get()

    if message.strip() != "" and client is not None:
        client.send(message)
        champ_message.delete(0, tk.END)

# bouton de connexion 
bouton_connexion = tk.Button(
    cadre_connexion,
    text="Connexion",
    command=connexion
)

bouton_connexion.grid(row=2, column=0, columnspan=3, pady=10)

# info client
info_client = tk.Label(page_chat, text="", bg="#1e2430", fg="white")
info_client.pack(pady=10)

# zone pour afficher les messages
zone_messages = tk.Text(page_chat, height=10, width=40, bg="#2b3444", fg="white")
zone_messages.pack(fill="both", expand=True, padx=10, pady=10)

afficher_messages() 

champ_message = tk.Entry(page_chat, width=40, bg="#2b3444", fg="white")
champ_message.pack(pady=5)

bouton_envoyer = tk.Button(page_chat, text="Envoyer", command=envoyer)
bouton_envoyer.pack(pady=5)

champ_message.bind("<Return>", lambda event: envoyer())

fenetre.mainloop() # reste ouverte jusqu'à ce qu'on la ferme
