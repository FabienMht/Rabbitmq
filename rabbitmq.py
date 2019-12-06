try:
    import pika,json,sys
    from flask import Flask, request
except ModuleNotFoundError as error:
    print(error.__class__.__name__ + ": " + error.name)
    exit(1)

# Variables
app = Flask(__name__)
rabbitmq_address=str(sys.argv[1])

def create(address,file):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=address))
    channel = connection.channel()
    channel.queue_declare(queue=file)
    connection.close()
    return True

def purge(address,file):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=address))
    channel = connection.channel()
    if channel.queue_declare(queue=file,passive=True):
        channel.queue_purge(queue=file)
    connection.close()
    return True
    
def write(address,msg,file):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=address))
    channel = connection.channel()
    channel.basic_publish(exchange='', routing_key=file, body=json.dumps(msg))
    connection.close()
    return True

def read(address,file):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=address))
    channel = connection.channel()
    method_frame, header_frame, body = channel.basic_get(file)
    if method_frame:
        print(method_frame, header_frame, body)
        channel.basic_ack(method_frame.delivery_tag)
        return body
    else:
        return "False"

# Test de connexion à la file Rabbitmq
try:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_address))
    connection.close()
except pika.exceptions.AMQPConnectionError:
    print("Erreur : connexion impossible a la file RabbitMq "+rabbitmq_address)
    exit(1)

# Définition des routes
@app.route("/rabbit/create",methods=['POST'])
def f1():
    file = json.loads(request.form["data"])
    
    if create(rabbitmq_address,file["file"]):
        return "Creation de la file termine"
    else:
        return "Erreur creation de file"

@app.route("/rabbit/sendmsg/<file_name>",methods=['POST'])
def f2(file_name=None):
    msg = json.loads(request.form["data"])
    
    if write(rabbitmq_address,msg,file_name):
        return "Message parti"
    else:
        return "Erreur envoi de message"

@app.route("/rabbit/getmsg/<file_name>",methods=['GET'])
def f4(file_name=None):
    return read(rabbitmq_address,file_name)

@app.route("/rabbit/purge",methods=['POST'])
def f3():
    file = json.loads(request.form["data"])
    
    if purge(rabbitmq_address,file["file"]):
        return "Purge de la file termine"
    else:
        return "Purge creation de file"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000,debug=True)

