import argparse
import threading
import sys
from app import BaseApp
from utils import Site
from utils import Message
from utils import informative_receiveMes
from queue import Queue

# cette classe est pour controler les messages entre les sites et entre les applications de base et les applications de contrôle
class controlApp(BaseApp):
    # Constructeur, ici on réecrire le constructeur de la classe mère, parce que on n'pas besion de dataHandler et operationExecuting
    def __init__(self, site_name:str, semaphore:threading.Semaphore, period:int, q:Queue, site:Site):
        self.site_name = site_name
        self.semaphore = semaphore
        self.period = period
        self.message_queue = q
        self.siteApp = site
        self.in_SC = False

    # cette fonction est appelée quand on veut envoyer un message, le message est mis dans la queue
    def send_message(self, msgType: str, sender, receiver, localhlg: int):
        self.message_queue.put(Message(msgType, sender, receiver, localhlg))

    # cette fonction est appelée quand on reçoit un message
    def receive_message(self, message: Message):
        if message.receiver == "0" and message.sender == f"A{self.siteApp.siteId}":
            msgAffichage = f"Type de Msg: {message.message_type} ; Sender: {message.sender} ; receiver: {self.site_name} ; LocalDate du sender: {message.hlg}"
            informative_receiveMes(self.site_name,msgAffichage)
        # si le msg est envoyé par BaseApp
            if message.message_type == "demandeSC":
                self.handle_demandeSC(message)
            if message.message_type == "finSC":
                self.handle_finSC(message)
        if message.receiver == str(self.siteApp.siteId) and message.sender != str(self.siteApp.siteId):
            msgAffichage = f"Type de Msg: {message.message_type} ; Sender: C{message.sender} ; receiver: C{message.receiver} ; LocalDate du sender: {message.hlg}"
            informative_receiveMes(self.site_name,msgAffichage)
            # si le site est le receiver
            if message.message_type == "requete":
                self.handle_requete(message)
            if message.message_type == "libération":
                self.handle_liberation(message)
            if message.message_type == "ack":
                self.handle_ack(message)


    # cette fonction est pour lancer les threads de send et receive
    def run(self):
        send_thread = threading.Thread(target=self._send_loop, args=())
        receive_thread = threading.Thread(target=self._receive_loop, args=())

        send_thread.start()
        receive_thread.start()

        send_thread.join()
        receive_thread.join()



    # ce fonction permet de vérifier si le site peut entrer dans la section critique, si oui on envoie un message "debutSC" au baseApp
    def checkDebutSC(self):
        if not self.in_SC and self.siteApp.tab[int(self.siteApp.siteId) - 1][0] == "requete" and all(
            (self.siteApp.tab[int(self.siteApp.siteId) - 1][1], int(self.siteApp.siteId)) < (self.siteApp.tab[k][1], k + 1)
            for k in range(len(self.siteApp.tab))
            if k != int(self.siteApp.siteId) - 1
        ):  # le condition dans all() est vérifié si (horloge_local,site_id) est plus petit à (horloge_local,site_id) de tous les autres sites
            self.send_message("debutSC", self.siteApp.siteId, 0, self.siteApp.localtime)
            self.in_SC = True
            # receiver = 0 signifie que le message est entre l'application de base et l'application de contrôle du même site

    '''les handlers pour les messages envoyés par baseApp
    -------------------------------------------------------------------------------------------
    '''
    def handle_demandeSC(self, message:Message):
        j = self.siteApp.siteId - 1
        self.siteApp.localtime += 1
        self.siteApp.tab[j] = ("requete", self.siteApp.localtime)
        # faire le diffussion
        # modifier le logique de diffusion si besoin en fonction de partie C
        for i in range(len(self.siteApp.tab)):
            if i != j:
                self.send_message("requete", self.siteApp.siteId, i+1, self.siteApp.localtime)


    def handle_finSC(self, message:Message):
        j = self.siteApp.siteId - 1
        self.siteApp.localtime += 1
        self.siteApp.tab[j] = ("libération", self.siteApp.localtime)
        # faire le diffussion
        # modifier le logique de diffusion si besoin en fonction de partie C
        for i in range(len(self.siteApp.tab)):
            if i != j:
                self.send_message("libération", self.siteApp.siteId, i+1, self.siteApp.localtime)
        self.in_SC = False


    '''les handlers pour les messages envoyés par les autres sites(controlApp)
    -------------------------------------------------------------------------------------------
    '''
    def handle_requete(self, message:Message):
    # Message reçu : requete
    # Traitement : mettre à jour le tableau de site et envoyer un message 'ack' au site qui a envoyé le message 'requete'
        j = int(message.sender) - 1
        self.siteApp.localtime = max(self.siteApp.localtime, message.hlg) + 1
        self.siteApp.tab[j] = ("requete", message.hlg)
        if not self.in_SC:
            self.send_message("ack", self.siteApp.siteId, message.sender, self.siteApp.localtime)
        # vérifier si le site peut entrer dans la section critique
            self.checkDebutSC()

    def handle_liberation(self, message:Message):
    # Message reçu : libération
    # Traitement : mettre à jour le tableau de site
        j = int(message.sender) - 1
        self.siteApp.localtime = max(self.siteApp.localtime, message.hlg) + 1
        self.siteApp.tab[j] = ("libération", message.hlg)
        # vérifier si le site peut entrer dans la section critique
        self.checkDebutSC()

    def handle_ack(self, message:Message):
        j = int(message.sender) - 1
        self.siteApp.localtime = max(self.siteApp.localtime, message.hlg) + 1
        if self.siteApp.tab[j][0] != "requete":
            self.siteApp.tab[j] = ("ack", message.hlg)
        # vérifier si le site peut entrer dans la section critique
        self.checkDebutSC()

def main():
    # récupérer les arguments
    flags = argparse.ArgumentParser()
    flags.add_argument("-i", "--id", type=int, required=True, help="id of the site")
    flags.add_argument("-p", "--period", type=int, required=True, help="Définir la période d'envoi des messages (en secondes), définir à 0 pour annuler l'envoi périodique")
    flags.add_argument("-N", "--nbSites", type=int, required=True, help="Nombre total de sites")
    flags.add_argument("-n", "--name", type=str, required=True, help="Définir le nom du site")
    args = flags.parse_args()

    # initialiser le site
    site = Site(args.id, args.nbSites)
    q = Queue()
    # initialiser le semaphore
    semaphore = threading.Semaphore(1)

    # lancer l'application de base
    ctlApp = controlApp(args.name, semaphore, args.period, q, site)
    ctlApp.run()

if __name__ == "__main__":
    main()
