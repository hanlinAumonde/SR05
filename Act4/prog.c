#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <fcntl.h>
#include <string.h>

//Solution : Utiliser sigaction et sigprocmask pour traiter, bloquer et debloquer le signal SIGIO


void ReadMessage(){
    char buf[64];
    if(fgets(buf,sizeof(buf),stdin) != NULL){  //Lire une chaîne/message (terminée par \n) à partir de stdin
        fprintf(stderr,"Message received : %s",buf);  //Afficher le message dans stderr
        /*
        //C'est pour verifier l'atomicite
        for(int i=0;i<1000;i++){
            fprintf(stderr,".");
            sleep(2);
        }
        */
    }
}

int main(int argc,char *argv[]){
    char *message = "Message\n"; //Message default envoyé
    if (argc > 1) {
        message = argv[1];
        strcat(message,"\n");  //On peut changer le message default 
    }
    
    //Définir la handler de traitement du signal SIGIO
    struct sigaction Mysig;
    Mysig.sa_handler = ReadMessage;
    sigemptyset(&Mysig.sa_mask);
    Mysig.sa_flags = 0;
    sigaction(SIGIO,&Mysig,NULL); 
    
    fcntl(STDIN_FILENO,F_SETFL,O_ASYNC); //Définir stdin (c'est-à-dire le descripteur de fichier STDIN_FILENO) en mode asynchrone (O_ASYNC)
    fcntl(STDIN_FILENO,F_SETOWN,getpid()); //Définir le propriétaire de l'entrée standard sur le processus en cours
    
    while(1){
        sigset_t masque, prev_masque;
        sigemptyset(&masque);
        sigaddset(&masque,SIGIO);
        
        sigprocmask(SIG_BLOCK,&masque,&prev_masque); // bloquer le SIGIO
        fprintf(stdout,"%s",message);
        fflush(stdout);
        sigprocmask(SIG_SETMASK,&prev_masque,NULL);  // debloquer le SIGIO
        
        sleep(5);
    }
    return 0;
}
