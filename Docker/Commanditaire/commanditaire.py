try:
    import requests,json,os,pika,sys
except ModuleNotFoundError as error:
    print(error.__class__.__name__ + ": " + error.name)
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
git_url_repo="https://github.com/FabienMht/N_dames.git"
commit_msg="RT704"
file_tache="ToDo"
file_resultat="Done"
flask_address="flask" # Nom DNS du container Flask grâce au lien entre les containeurs docker
rabbitmq_address="rabbitmq" # Nom DNS du container Rabbitmq grâce au lien entre les containeurs docker
nb_taches=[]
resultat=0

# Tant que le serveur rabbitmq n'est pas joignable le reste du code n'est pas éxécuté
os.system("""curl --silent rabbitmq:5672 > /dev/null
while [[ "$?" = "7" ]]; do
  sleep 1
  curl --silent rabbitmq:5672 > /dev/null
done""")

# Tant que le serveur flask n'est pas joignable le reste du code n'est pas éxécuté
os.system("""curl --silent flask:5000 > /dev/null
while [[ "$?" = "7" ]]; do
  sleep 1
  curl --silent flask:5000 > /dev/null
done""")

# Test du paramètre qui définie la taille de l'échiquier
chess_size=int(os.environ['TAILLE'])

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

sol=[-1]*chess_size

# Génération des taches
for i in range(chess_size):
    sol[0]=i
    tache={}
    tache["ID_projet"] = 1
    tache["ID_tache"] = i
    tache["URL_git"] = git_url_repo
    tache["CMD"] = "python3 /n_dame.py "+str(sol).replace(" ","")
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
