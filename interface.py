import tkinter as tk
from tkinter import messagebox
from client import Client, add_server, change_user_count
import queue
import json

client = None
port_choisi = None
messages = queue.Queue()

# fenêtre principale
fenetre = tk.Tk()
fenetre.title("Chat")
fenetre.geometry("500x400")
fenetre.configure(bg="#1e2430")

# page serveurs
page_serveurs = tk.Frame(fenetre, bg="#1e2430")
page_serveurs.pack(fill="both", expand=True)

# page connexion
page_connexion = tk.Frame(fenetre, bg="#1e2430")

# page chat
page_chat = tk.Frame(fenetre, bg="#1e2430")


# récup les serveurs 
def charger_serveurs():
    try:
        with open("serverslist.json", "r") as f:
            serveurs = json.load(f)
        return serveurs
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# met à jour le nombre d'utilisateurs
def modifier_compteur(port, deconnexion=False):
    serveurs = charger_serveurs()
    for serveur in serveurs:
        if serveur["port"] == port:
            if deconnexion:
                serveur["count"] = max(0, serveur["count"] - 1)
            else:
                serveur["count"] += 1

            break
    with open("serverslist.json", "w") as f:
        json.dump(serveurs, f)

# affiche les serveurs 
def afficher_serveurs():
    serveurs = charger_serveurs()
    selection = liste_serveurs.curselection()
    port_selectionne = None
    if selection:
        port_selectionne = liste_serveurs.get(selection[0]).split()[2]
    liste_serveurs.delete(0, tk.END)
    for i, serveur in enumerate(serveurs):
        liste_serveurs.insert(
            tk.END,
            f"Port : {serveur['port']} - {serveur['count']} connectés"
        )
        if str(serveur["port"]) == port_selectionne:
            liste_serveurs.selection_set(i)
    fenetre.after(2000, afficher_serveurs)


# récupère le serveur
def choisir_serveur():
    global port_choisi
    selection = liste_serveurs.curselection()
    if not selection:
        messagebox.showerror("Erreur", "Choisis un serveur")
        return
    serveurs = charger_serveurs()
    if selection[0] >= len(serveurs):
        messagebox.showerror("Erreur", "La liste a changé")
        return
    port_choisi = serveurs[selection[0]]["port"]
    page_serveurs.pack_forget()
    page_connexion.pack(fill="both", expand=True)

# crée un serveur
def creer_serveur():
    global port_choisi
    try:
        port_choisi = add_server()
        page_serveurs.pack_forget()
        page_connexion.pack(fill="both", expand=True)
    except OSError:
        messagebox.showerror("Erreur", "Impossible de créer le serveur")
        
# fonction connection
def connexion():
    global client
    if client is not None:
        messagebox.showwarning("Attention", "Tu es déjà connecté")
        return
    username = champ_username.get()
    server = "127.0.0.1"
    port = port_choisi
    if username.strip() == "":
        messagebox.showerror("Erreur", "Le pseudo ne peut pas être vide")
        return
    if port is None:
        messagebox.showerror("Erreur", "Choisis un serveur")
        return
    try:
        client = Client(username, server, port)
        client.afficher_message = messages.put
        client.listen()
        modifier_compteur(port)
    except OSError:
        client = None
        messagebox.showerror("Erreur", "Impossible de se connecter")
        return
    info_client.config(
        text=f"Pseudo : {username} | IP : {server} | Port : {port}"
    )
    zone_messages.delete("1.0", tk.END)
    page_connexion.pack_forget()
    page_chat.pack(fill="both", expand=True)


# fonction déconnecter
def deconnexion():
    global client, port_choisi
    if client is not None:
        if client.listening:
            client.send("QUIT")
    modifier_compteur(port_choisi, True)
    client = None
    page_chat.pack_forget()
    page_connexion.pack_forget()
    page_serveurs.pack(fill="both", expand=True)


# fonction envoie message
def envoyer():
    message = champ_message.get()

    if message.strip() != "" and client is not None and client.listening:
        client.send(message)
        champ_message.delete(0, tk.END)


# affiche les messages
def afficher_messages():
    while not messages.empty():
        message = messages.get()
        zone_messages.insert(tk.END, message + "\n")
        zone_messages.see(tk.END)

    if client is not None and not client.listening:
        deconnexion()

    fenetre.after(100, afficher_messages)

label_serveurs = tk.Label(
    page_serveurs,
    text="Serveurs disponibles :",
    bg="#1e2430",
    fg="white"
)
label_serveurs.pack(pady=10)

liste_serveurs = tk.Listbox(page_serveurs, width=40, height=5)
liste_serveurs.pack(pady=5)

bouton_rejoindre = tk.Button(
    page_serveurs,
    text="Rejoindre",
    command=choisir_serveur
)
bouton_rejoindre.pack(pady=10)

# bouton créer un serveur
bouton_creer = tk.Button(
    page_serveurs,
    text="Créer un serveur",
    command=creer_serveur
)
bouton_creer.pack(pady=5)

cadre_connexion = tk.Frame(page_connexion, bg="#2b3444")
cadre_connexion.pack(pady=30)

label_username = tk.Label(
    cadre_connexion,
    text="Pseudo :",
    bg="#2b3444",
    fg="white"
)
label_username.pack(pady=5)

champ_username = tk.Entry(cadre_connexion, width=25)
champ_username.pack(pady=5)

bouton_connexion = tk.Button(
    cadre_connexion,
    text="Connexion",
    command=connexion
)
bouton_connexion.pack(pady=10)


# info client
info_client = tk.Label(
    page_chat,
    text="",
    bg="#1e2430",
    fg="white"
)
info_client.pack(pady=10)

# bouton déconnexion
bouton_deconnexion = tk.Button(
    page_chat,
    text="Déconnexion",
    command=deconnexion
)
bouton_deconnexion.pack(pady=5)

zone_messages = tk.Text(
    page_chat,
    height=10,
    width=40,
    bg="#2b3444",
    fg="white"
)
zone_messages.pack(fill="both", expand=True, padx=10, pady=10)

cadre_message = tk.Frame(page_chat, bg="#1e2430")
cadre_message.pack(fill="x", padx=10, pady=10)

champ_message = tk.Entry(
    cadre_message,
    bg="#2b3444",
    fg="white"
)
champ_message.pack(side="left", fill="x", expand=True, padx=5)

bouton_envoyer = tk.Button(
    cadre_message,
    text="Envoyer",
    command=envoyer
)
bouton_envoyer.pack(side="right")

champ_message.bind("<Return>", lambda event: envoyer())

afficher_serveurs()
afficher_messages()

fenetre.mainloop()