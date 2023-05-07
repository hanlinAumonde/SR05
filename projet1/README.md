# sr05 projet groupe

# Zoo Network Project

Ce projet simule un système distribué pour un zoo, où les animaux sont situés dans différents sites (A1, A2, A3). Le projet est composé de plusieurs fichiers Python, d'un script shell et d'un fichier JSON pour stocker les données partagées.

## Description des fichiers


## app.py
L'application principale pour la gestion des sites de zoo. Il lit et traite les messages entrants et envoie les messages sortants. L'utilisateur réalise la demande d'accès aux données via le bouton d'une interface graphique simple, et sélectionne le type d'opération et effectue l'opération de données via une interface graphique après avoir obtenu l'autorisation.

## ctl.py
L'application de contrôle envoie des commandes à la station pour permettre à l'application de base de commencer à déplacer les animaux ou de demander une liste d'animaux. Il est également connecté à d'autres applications de contrôle et réalise un accès mutuellement exclusif à la section critique via un algorithme de file d'attente.

## utils.py
Contient diverses classes et méthodes nécessaires requises par le programme, telles que l'envoi d'informations, etc.

## data_sample.JSON
Enregistrez les données qui doivent être partagées et stockez le nom de l'animal et le numéro du zoo auquel il appartient sous la forme de paires clé-valeur.

## reseauMKFIFO.sh
Contient des commandes shell pour créer le réseau et la possibilité de nettoyer les pipelines créés après la fin du programme.

## Comment courir
 - Assurez-vous que Python 3 est installé sur votre système.
 - Assurez-vous que tous les fichiers se trouvent dans le même répertoire.

Donner des autorisations exécutables au script shell

```
chmod +x reseauMKFIFO.sh
```
- Lancer le programme :
```
./reseauMKFIFO.sh
```

