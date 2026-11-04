import ipaddress


def validateUsername():
    """Vérifie que l'username entré par l'utilisateur n'est pas vide. Si l'username est vide, il redemande à l'utilisateur de saisir un username valide."""
    while True:
        try:
            username= input("username: ")
            if username.strip() == "":
                raise ValueError("Username cannot be empty.")
            return username
        except ValueError as e:
            print(f"Invalid input. Please enter a valid username. Error: {e}")
            continue

def validateServer():
    """Vérifie que l'adresse IP du serveur entrée par l'utilisateur est valide."""
    while True:
        try:
            server= input("server: ")
            ipTest = ipaddress.ip_address(server)  # si l'adresse IP est invalide, une exception sera levée
            return server
        except (ipaddress.AddressValueError, ValueError) as e:
            print(f"Invalid IP address. Please enter a valid IP address. Error: {e}")
            continue

def validatePort():
    """Vérifie que le port entré par l'utilisateur est valide."""
    while True:
        try:
            port= int(input("port: "))
            return port
        except ValueError as e:
            print(f"Invalid input. Please enter a valid port. Error: {e}")
            continue