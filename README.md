# Script
## Prérequis

### Worker
**Paquets :**
- Docker
- Python3 avec le module venv
- Git

### Commanditaire
**Paquets :**
- Docker pour rabbitmq
- Python3 avec le module venv
- Git

## Execution
**Etapes :**
1. Cloner le dépot rabbitmq : git clone https://github.com/FabienMht/Rabbitmq.git
2. Chnager les droits des script : chmod +x launch_*
3. Initialiser le projet :
    1. Commanditaire : sudo ./launch_com.sh -i
    2. Worker : sudo ./launch_worker.sh -i
4. Lancer le code :
    1. Commanditaire : sudo ./launch_com.sh -s x (où x est la taille de l'échiquier)
    2. Worker : sudo ./launch_worker.sh -s ip_address (où ip_address est l'adresse ip du serveur flask, dans ce cas l'ip du commanditaire)
5. Nettoyer le projet :
    1. Commanditaire : sudo ./launch_com.sh -d
    2. Worker : sudo ./launch_worker.sh -d

# Docker compose
## Prérequis

**Paquets :**
- Docker
- Docker-compose
- Git

## Execution
**Etapes :**
1. Cloner le dépot rabbitmq : git https://github.com/FabienMht/Rabbitmq.git
2. Lancer les services en root : 
    1. Première initialisation : export TAILLE=X && sudo -E docker-compose up (ou x correspond à la taille de l'échiquier)
    2. Sinon : sudo -E docker-compose up
3. Afficher les logs : sudo docker-compose logs
4. Arrêter les services : sudo docker-compose down
