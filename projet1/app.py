import argparse
import threading
import sys
import time
import re
import tkinter as tk
from tkinter import messagebox
from utils import DataHandler, Message , check_MsgFormat, informative_receiveMes, informative_sendMes
from queue import Queue

# BaseApp est la classe mère de controlApp et baseApp
class BaseApp:
    def __init__(self, site_name:str, semaphore:threading.Semaphore, period:int, siteNb:int, q:Queue, dataHandler:DataHandler):
        self.site_name = site_name
        self.semaphore = semaphore
        self.period = period
        self.siteNb = siteNb
        self.message_queue = q
        self.operationExecuting = False # pour savoir si l'application est en train d'exécuter une opération
        self.dataHandler = dataHandler

    # cette fonction est appelée quand on veut envoyer un message, le message est mis dans la queue
    def send_message(self, msgType:str, dest, originHlg:int):
        self.message_queue.put(Message(msgType, self.site_name, dest, originHlg))

    # cette fonction est appelée quand on reçoit un message
    def receive_message(self, message:Message):
        if message.message_type == "debutSC" and f"A{message.sender}" == self.site_name:
            if self.operationExecuting:
                msgAffichage = f"Type de Msg: {message.message_type} ; Sender: C{message.sender} ; receiver: {self.site_name} ; LocalDate du sender: {message.hlg}"
                informative_receiveMes(self.site_name,msgAffichage)
                self.handle_debutSC(message)
            elif not self.operationExecuting:
                self.dataHandler.refresh_local_animals()
                self.send_message("finSC", 0, message.hlg)
            
            

    # cette fonction crée 2 threads pour envoyer et recevoir des messages, et un thread pour demander à l'utilisateur s'il veut entrer dans la section critique
    # le dernier thread n'a pas besion de semaphore parce qu'il s'agit d'une interaction avec l'utilisateur
    def run(self):
        
        send_thread = threading.Thread(target=self._send_loop, args=())
        receive_thread = threading.Thread(target=self._receive_loop, args=())
        prompt_thread = threading.Thread(target=self._prompt_user, args=())
        refresh_thread = threading.Thread(target=self._refresh_loop,args=())

        send_thread.start()
        receive_thread.start()
        prompt_thread.start()
        refresh_thread.start()

        send_thread.join()
        receive_thread.join()
        prompt_thread.join()
        refresh_thread.join()
        

    # cette fonction est pour envoyer des messages
    def _send_loop(self):
        while True:
            if not self.message_queue.empty():
                message = self.message_queue.get()
                with self.semaphore:
                    if message.receiver != 0:
                        rcv = f"C{message.receiver}"
                    elif message.message_type == "debutSC":
                        rcv = f"A{message.sender}"
                    else:
                        siteID = int(re.findall(r'\d+', self.site_name)[0])
                        rcv = f"C{siteID}"
                    msgAffichage = f"Type de Msg: {message.message_type} ; Send to: {rcv}"
                    informative_sendMes(self.site_name,msgAffichage)
                    sys.stdout.write(f"{message.serialize()}\n")
                    sys.stdout.flush()
            if self.period > 0:
                time.sleep(self.period)

    # cette fonction est pour recevoir des messages, l'execution du reception et envoi est sequentiel
    def _receive_loop(self):
        while True:
            received_message = sys.stdin.readline().strip()
            with self.semaphore:
                if received_message and check_MsgFormat(received_message):
                    received_message = Message.deserialize(received_message)
                    self.receive_message(received_message)
            if self.period > 0:
                time.sleep(self.period)


    # cette fonction est pour demander à l'utilisateur s'il veut entrer dans la section critique
    def _prompt_user(self):
        def on_request_button_click():
            #if not self.operationExecuting:
            self.send_message("demandeSC", 0, 0)
            self.operationExecuting = True
            self.request_button.config(state="disabled")
        
        def Update():
            displayed_data.set("Animaux actuels sur le site: " + ', '.join(self.dataHandler.local_animals))

        root = tk.Tk()
        root.title(f"User interface du {self.site_name}")
        root.geometry("300x200")

        display = tk.Frame(root)
        displayed_data = tk.StringVar()
        displayed_data.set("Animaux actuels sur le site: " + ', '.join(self.dataHandler.local_animals))
        displated_label = tk.Label(root,textvariable=displayed_data)
        displated_label.pack(fill="both",expand=True)
        update_button = tk.Button(root,text="Update",command=Update)
        update_button.pack(fill="both",expand=True)

        request_frame = tk.Frame(root)
        self.request_button = tk.Button(request_frame, text="Demander un accès à la section critique", command=on_request_button_click)
        self.request_button.pack(fill="both", expand=True)
        request_frame.pack(fill="both", expand=True)

        root.mainloop()
    
    def _refresh_loop(self):
        while True:
            self.send_message("demandeSC", 0, 0)
            time.sleep(15)

    '''le handler pour traiter le message 'debutSC' envoyé par controlApp'''
    def handle_debutSC(self, message: Message):
        
        def on_transfer_button_click():
            animal_name = animal_name_entry.get()
            new_site = new_site_entry.get()
            self.dataHandler.transfer_Animal(animal_name, new_site)
            messagebox.showinfo("Succès", "L'animal a été transféré avec succès\n liste des animaux actuels : " + ', '.join(self.dataHandler.local_animals))
            temp_root.destroy()

        def on_refresh_button_click():
            self.dataHandler.refresh_local_animals()
            messagebox.showinfo("Succès", "Les données locales ont été rafraîchies avec succès\n liste des animaux actuels : " + ', '.join(self.dataHandler.local_animals))
            temp_root.destroy()

        temp_root = tk.Tk()
        temp_root.title(f"Opération du site {self.site_name}")
        temp_root.geometry("500x300")

        if self.dataHandler.local_data:
        # Lors du premier accès aux données partagées, seules les données locales sont mises à jour et aucune opération n'est effectuée
            
            transfer_frame = tk.Frame(temp_root)
            animal_name_label = tk.Label(transfer_frame, text="Nom de l'animal:")
            animal_name_label.grid(row=0, column=0, padx=(10, 5), pady=(10, 0))
            animal_name_entry = tk.Entry(transfer_frame)
            animal_name_entry.grid(row=0, column=1, padx=(5, 10), pady=(10, 0))

            new_site_label = tk.Label(transfer_frame, text="Site de destination:")
            new_site_label.grid(row=1, column=0, padx=(10, 5), pady=(10, 0))
            
            new_site_entry = tk.Entry(transfer_frame)
            new_site_entry.grid(row=1, column=1, padx=(5, 10), pady=(10, 0))

            transfer_button = tk.Button(transfer_frame, text="Transférer un animal à un autre site", command=on_transfer_button_click)
            transfer_button.grid(row=2, column=0, columnspan=2, pady=(10, 10))
            transfer_frame.pack(fill="both", expand=True)

        refresh_frame = tk.Frame(temp_root)
        refresh_button = tk.Button(refresh_frame, text="Rafraîchir les données locales", command=on_refresh_button_click)
        refresh_button.pack(fill="both", expand=True)
        refresh_frame.pack(fill="both", expand=True)

        temp_root.mainloop()

        self.send_message("finSC", 0, message.hlg)  # envoyer un message pour dire que l'opération est terminée
        self.operationExecuting = False  # l'opération est terminée, on peut demander à l'utilisateur de choisir une autre opération
        self.request_button.config(state="normal")
        


def main():
    # parser les arguments
    flags = argparse.ArgumentParser(description="Process some integers.")
    flags.add_argument("-p", "--period", type=int, default=2, help="Définir la période d'envoi des messages (en secondes), définir à 0 pour annuler l'envoi périodique")
    flags.add_argument("-n", "--name", type=str, required=True, help="Définir le nom du site")
    flags.add_argument("-N", "--nbSites", type=int, required=True, help="Nombre total de sites")
    args = flags.parse_args()

    # initialiser les variables
    semaphore = threading.Semaphore(1)
    q = Queue()
    # Ici, on doit initialiser le dataHandler avant l'initialisation de baseApp, avec le path du fichier json, chaque site a l'accès au même fichier json
    dataHandler = DataHandler(args.name,"data_sample.json")

    # initialiser l'application de base
    baseApp = BaseApp(args.name, semaphore, args.period,args.nbSites, q, dataHandler)
    baseApp.run()


if __name__ == "__main__":
    main()

