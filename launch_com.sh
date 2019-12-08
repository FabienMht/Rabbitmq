#!/bin/bash

usage () {

  echo ""
  echo "Usage: ./launch_com.sh"
  echo ""
  echo "Prérequis pour le script : docker, python3, module venv pour python3 et git"
  echo ""
  echo "Options"
  echo "  --start, -s  taille_n_dame    : Lance le code du commanditaire"
  echo "  --init, -i                    : Initialise le code du comanditaire"
  echo "  --delete, -d                  : Supprime le code du comanditaire"
  echo "  --help, -h                    : Aide"
  echo ""

}

if [[ "$EUID" -ne 0 ]]; then 
  echo "Lancer le script en tant que root"
  usage
  exit 1
fi

# Variables
START=0
TAILLE_DAME=0
INIT=0
DELETE=0
basedir=$(dirname $0)

if [[ "$1" = "" ]]; then
  usage
  exit 1
fi

while [ "$1" != "" ];
do
  case "$1" in
    --start | -s )      START=1
                        if [[ $2 = "" ]]; then
                          usage
                          exit 1
                        fi
                        TAILLE_DAME=$2
                        shift;;
    --init | -i )       INIT=1
                        ;;
    --delete | -d )     DELETE=1
                        ;;
    --help | -h )       usage
                        ;;  
    * )                 echo "Paramètre $1 non disponible !"
                        usage
                        exit 1
  esac
  shift
done

echo "Time start : $(date +"%T")"
echo "############# Script Commanditaire ##############"
echo -e "  -  Choix options :
        -  Start : $START
        -  Init : $INIT
        -  Delete : $DELETE\n"

if [[ $INIT = 1 ]]; then

  type docker > /dev/null
  if [[ "$?" = "1" ]]; then
    echo "Installez docker"
  fi
  type python3 > /dev/null
  if [[ "$?" = "1" ]]; then
    echo "Installez python3"
  fi
  type git > /dev/null
  if [[ "$?" = "1" ]]; then
    echo "Installez git"
  fi
  python3 -c 'print (help("modules"))' | grep venv > /dev/null
  if [[ "$?" = "1" ]]; then
    echo "Installez le module venv pour python3"
  fi

  Folder_UUID=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 10 | head -n 1)
  Folder_name="$basedir/Commanditaire_$Folder_UUID"

  python3 -m venv $Folder_name
  source $Folder_name/bin/activate
  pip3 install flask gitpython requests pika

  cp "$basedir/commanditaire.py" $Folder_name/
  cp "$basedir/rabbitmq.py" $Folder_name/

  rabbit_test=$(docker images | grep "rabbitmq:management")
  if [[ ! rabbit_test ]]; then
    docker pull rabbitmq:management
  fi

  echo "Folder_name=$Folder_name" > ./env.conf
  
fi

if [[ $START = 1 ]]; then

  if [[ -f $basedir/env.conf ]]; then
    source $basedir/env.conf
  else
    echo "Le projet n'est pas initialisé"
    usage
    exit 1
  fi

  container=$(docker run -d rabbitmq:management)
  container_address=$(docker inspect $container | grep '"IPAddress"' | head -1 | cut -d '"' -f 4)

  echo "Création du container rabbitmq : $container_address"

  curl --silent $container_address:5672 > /dev/null
  while [[ "$?" = "7" ]]; do
    sleep 1
    curl --silent $container_address:5672 > /dev/null
  done

  source $Folder_name/bin/activate

  nohup python3 $Folder_name/rabbitmq.py "$container_address" &
  flask_process=$(echo $!)

  echo "Lancement du serveur Flask"

  curl --silent localhost:5000 > /dev/null
  while [[ "$?" = "7" ]]; do
    sleep 1
    curl --silent localhost:5000 > /dev/null
  done

  python3 $Folder_name/commanditaire.py "$container_address" $TAILLE_DAME

  echo "Suppression du container et arrêt du serveur Flask"

  kill $flask_process
  sudo docker stop $container > /dev/null
  sudo docker rm $container > /dev/null
  rm $basedir/nohup.out

fi

if [[ $DELETE = 1 ]]; then
  
  if [[ -f $basedir/env.conf ]]; then
    source $basedir/env.conf
    rm -Rf $Folder_name
    rm $basedir/env.conf
    echo "Suppression du projet terminée"
  else
    echo "Le projet n'est pas initialisé"
    usage
    exit 1
  fi
  
fi

echo -e "\n######### Script terminé sans erreur #########"
echo "Time finish : $(date +"%T")"
