try:
    import requests,json,docker,time,sys,os
    from git import Repo,Actor
except ModuleNotFoundError as error:
    print(error.__class__.__name__ + ": " + error.name)
    exit(1)

def get_tache(address,file):
    try:
        r = requests.get("http://"+address+":5000/rabbit/getmsg/"+file)
    except Exception as e:
        return "False"
    return r.text

def send_msg(address,resultat,file):
    param = {"data" : json.dumps(resultat)}
    r = requests.post("http://"+address+":5000/rabbit/sendmsg/"+file,data=param)
    print(r.text)

def clone_repo(git_url,repo_dir):
    try:
        repo = Repo(repo_dir)
        for url in repo.remotes.origin.urls:
            if url==git_url:
                print("Dépot "+(git_url.split('/')[-1]).replace('.git','')+" déjà cloné dans "+repo.working_dir)
    except Exception as e:
        repo = Repo.clone_from(git_url, repo_dir)
        print("Dépot "+(git_url.split('/')[-1]).replace('.git','')+" cloné dans "+repo.working_dir)
    return repo
    
def pull_repo(repo):
    repo.remotes.origin.pull()
    print("Pull effectué")
    
def exec_container(client,image_name,command,detach):
    cont=client.containers.run(image=image_name, command=command, detach=detach, auto_remove=True)
    print("Container lancé")
    return cont
    
def build_container(client,path,tag):
    client.images.build(path=path,tag=tag)
    print("Build effectué")

# Variables
client = docker.from_env()
image_name = "rt704"
repo_workdir = "/N_Dames"
file_tache="ToDo"
file_resultat="Done"
flask_address="flask"

# Check flask connexion
os.system("""curl --silent flask:5000 > /dev/null
while [[ "$?" = "7" ]]; do
  sleep 1
  curl --silent flask:5000 > /dev/null
done""")

#time.sleep(5)

# Code
try:
    while True:
        tache = get_tache(flask_address,file_tache)
        if tache!="False" or tache!="Erreur":
            print(tache)
            tache_json = json.loads(tache)
            repo=clone_repo(tache_json["URL_git"],repo_workdir)
            pull_repo(repo)
            build_container(client,repo_workdir,image_name)
            resultat=exec_container(client,image_name,tache_json["CMD"],False)
            resultat_json={}
            resultat_json["ID_projet"] = int(tache_json["ID_projet"])
            resultat_json["ID_tache"] = int(tache_json["ID_tache"])
            resultat_json["Resultat"] = resultat.decode().strip('\n')
            print(resultat_json)
            send_msg(flask_address,resultat_json,file_resultat)
        else:
            print("Aucune tache !")
            exit(0)
        time.sleep(1)
except KeyboardInterrupt:
    print("Fin")
