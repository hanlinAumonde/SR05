import json
import sys
import re

def informative_receiveMes(site_name, message):

    sys.stderr.write('\033[92m' + "Site " + site_name + " ---> Received a message : " + message + '\033[0m' + '\n')
    sys.stderr.flush()

def informative_sendMes(site_name, message):

    sys.stderr.write('\033[95m' + "Site " + site_name + " ---> Send a message : " + message + '\033[0m' + '\n')
    sys.stderr.flush()


# cette classe représente le structure d'un message
class Message:
    def __init__(self, message_type:str, sender, receiver, hlg:int):
        self.message_type = message_type
        self.sender = sender
        self.receiver = receiver
        self.hlg = hlg

    def serialize(self):
        # Sérialiser le message en une chaîne de caractères avec des paires clé-valeur et des séparateurs
        return f",=snd={self.sender},=rcv={self.receiver},=hlg={self.hlg},=type={self.message_type}"

    @classmethod # c'est un decorateur pour definir une methode de classe
    def deserialize(cls, message_str):
        # Désérialiser la chaîne de caractères en fonction des '=' et des ',' pour créer un objet Message
        fields = message_str.split(",")[1:]
        field_dict = {}
        for field in fields:
            key, value = field.split("=")[1:]
            field_dict[key] = value
        # le mot-cle 'cls' est pour creer un objet de la classe 'Message' en utilisant le constructeur de la classe
        return cls(field_dict["type"], field_dict["snd"], field_dict["rcv"], int(field_dict["hlg"]))


class Site:
    # cet classe représente un site dans le réseau
    def __init__(self, siteId:int, N:int):
        self.siteId = siteId
        self.localtime = 0
        self.tab = [("libération", 0)] * N

# cette classe est pour gérer les données partagées
class DataHandler:
    def __init__(self, site_name: str, shared_data_file: str):
        self.site_name = site_name
        self.shared_data_file = shared_data_file
        self.local_animals = [] # les animaux qui sont dans le site
        self.local_data = {}    # le replicat des données partagées

    # charger les données partagées
    def load_sharedData(self):
        with open(self.shared_data_file, 'r') as file:
            data = json.load(file)
        return data

    # sauvegarder les données partagées depuis la mémoire locale
    def save_sharedData(self):
        with open(self.shared_data_file, 'w') as file:
            json.dump(self.local_data, file)

    # retourner les animaux qui sont dans le site
    def get_local_animals(self):
        return [animal for animal, site in self.local_data.items() if site == self.site_name]

    # rafranchir le replicat des données partagées
    def refresh_local_animals(self):
        self.local_data = self.load_sharedData()
        self.local_animals = self.get_local_animals()

    # transferer un animal vers un autre site
    def transfer_Animal(self, animal_name: str, new_site: str):
        self.refresh_local_animals()
        if animal_name in self.local_animals and new_site != self.site_name:
        # condition: l'animal est dans le site et le site de destination est différent du site actuel
            self.local_data[animal_name] = new_site
            self.save_sharedData()
            self.local_animals.remove(animal_name)

def check_MsgFormat(msg):
    pattern = r",=snd=(.*),=rcv=(.*),=hlg=(.*),=type=(.*)"
    match = re.match(pattern, msg)
    if match:
        return True
    else:
        return False
