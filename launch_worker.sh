#!/bin/bash

usage () {

  echo ""
  echo "Usage: ./launch_worker.sh"
  echo ""
  echo "Prérequis pour le script : docker, python3, module venv pour python3 et git"
  echo ""
  echo "Options"
  echo "  --start, -s    : Lance le code du worker"
  echo "  --init, -i     : Initialise le code du worker"
  echo "  --delete, -d   : Supprime le code du worker"
  echo "  --help, -h     : Aide"
  echo ""

}

if [[ "$EUID" -ne 0 ]]; then 
  echo "Lancer le script en tant que root"
  exit 1
fi

# Variables
START=0
INIT=0
DELETE=0
FLASK_ADDRESS=""
basedir=$(dirname $0)

if [[ "$1" = "" ]]; then
  usage
  exit 1
fi

while [ "$1" != "" ];
do
  case "$1" in
    --start | -s )      START=1
                        if [[ "$2" = "" ]]; then
                          usage
                          exit 1
                        fi
                        FLASK_ADDRESS="$2"
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
echo "############# Script Worker ##############"
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
  Folder_name="$basedir/Worker_$Folder_UUID"

  python3 -m venv $Folder_name
  source $Folder_name/bin/activate
  pip3 install gitpython requests docker
  deactivate

  cp "$basedir/worker.py" $Folder_name/

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
  
  echo "Test du serveur Flask"

  curl --silent $FLASK_ADDRESS:5000 > /dev/null
  if [[ "$?" = "7" ]]; then
    echo "Le serveur Flask est injoignable"
    usage
    exit 1
  fi

  source $Folder_name/bin/activate
  python3 $Folder_name/worker.py "$FLASK_ADDRESS" "$Folder_name"

  echo "Fin du worker"
  deactivate

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
