try:
    import requests,json,os,pika,sys
    from git import Repo,Actor
except ModuleNotFoundError as error:
    print(error.__class__.__name__ + ": " + error.name)
    exit(1)

def help():
    print("Utilisation : python3 commanditaire.py x (ou x est la taille de l echiquier)")
    exit(1)

def create_file(address,file):
    param = {"data" : json.dumps(file)}
    r = requests.post("http://"+address+":5000/rabbit/create",data=param)
    print(r.text)

def purge_file(address,file):
    param = {"data" : json.dumps(file)}
    r = requests.post("http://"+address+":5000/rabbit/purge",data=param)
    print(r.text)

def send_msg(address,tache,file):
    param = {"data" : json.dumps(tache)}
    r = requests.post("http://"+address+":5000/rabbit/sendmsg/"+file,data=param)
    print(r.text)
    print(tache)

def on_msg(channel, method, properties, body):
    global resultat
    print (body)
    resultat_json=json.loads(body.decode())
    resultat_temp=resultat_json["Resultat"]
    resultat_id_tache=resultat_json["ID_tache"]
    nb_taches.remove(int(resultat_id_tache))
    resultat=resultat+int(resultat_temp)
    
    if len(nb_taches)==0:
        channel.stop_consuming()
    
# Variables
author = Actor("Fabien M", "mauhouratfabien@gmail.com")
git_url_repo="git@github.com:FabienMht/Rabbitmq.git"
repo_workdir="./Project/Rabbitmq"
project_files="./Project/Files"
commit_msg="RT704"
file_tache="ToDo"
file_resultat="Done"
flask_address="localhost"
rabbitmq_address=str(sys.argv[1])
nb_taches=[]
resultat=0

# Test du paramètre qui définie la taille de l'échiquier
try:
    chess_size=int(sys.argv[2])
except IndexError:
    help()

# Test de connexion à la file Rabbitmq
try:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_address))
    connection.close()
except pika.exceptions.AMQPConnectionError:
    print("Erreur : connexion impossible a la file RabbitMq "+rabbitmq_address)
    exit(1)

# Création des files
for list in file_tache,file_resultat:
    file={}
    file["file"] = list
    purge_file(flask_address,file)
    create_file(flask_address,file)

# Génération des taches
for i in range(chess_size):
    tache={}
    tache["ID_projet"] = 1
    tache["ID_tache"] = i
    tache["URL_git"] = git_url_repo
    tache["CMD"] = "python3 /n_dame.py ["+str(i)+",-1,-1,-1,-1,-1,-1,-1]"
    nb_taches.append(int(tache["ID_tache"]))
    send_msg(flask_address,tache,file_tache)

connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_address))
channel = connection.channel()
print("En attente de message")
channel.basic_consume(file_resultat,on_msg,auto_ack=True)
try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
connection.close()

print("Nombre de solutions :",resultat)
