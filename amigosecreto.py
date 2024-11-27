import random
import string
import json

from flask import Flask, jsonify, render_template, request


app = Flask(__name__)
URL = "https://innacroft.pythonanywhere.com"

@app.route('/add_participants', methods=['GET', 'POST'])
def add_participants():
    if request.method == 'POST':
        participants = request.form.get('participants')

        if not participants:
            return jsonify({"error": "Participants were not sent."}), 400

        participants = [p.strip() for p in participants.split(',') if p.strip()]

        asignations = assign_secret_friend(participants)
        custom_urls = create_links(asignations)
        return custom_urls

    return '''
        <form method="post">
        <label for="participants">Participants (Separated by commas):</label><br>
        <textarea name="participants" rows="4" cols="50"></textarea><br>
        <button type="submit">START</button>
    </form>
    '''

def assign_secret_friend(participants):
    friends = participants[:]
    random.shuffle(friends)
    
    while any(p == a for p, a in zip(participants, friends)):
        random.shuffle(friends)
    
    return dict(zip(participants, friends))

def create_links(asignations):
    
    enlaces = {}
    enlaces_show = {}
    
    for participant, friend in asignations.items():
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=8))  # Generar un token único
        link = f"{URL}/reveal?token={token}"
        enlaces[token] = {"participant": participant, "friend": friend, "used": False}
        enlaces_show[participant] = f"Click here to reveal your christmas friend: {link}"
    with open("friends_secret.json", "w") as file:
        json.dump(enlaces, file, indent=4)
    return enlaces_show

@app.route("/reveal", methods=["GET"])
def reveal():
    token = request.args.get("token")
    
    if not token:
        return "<h1>Token is not found</h1><p>Please make sure you have the correct link.</p>", 400
    
    try:
        with open("friends_secret.json", "r") as file:
            enlaces = json.load(file)
    except FileNotFoundError:
        return "<h1>Error loading asignations</h1><p>Not found assignations file.</p>", 500
    
    if token not in enlaces:
        return "<h1>Invalid linko</h1><p>Token is not valid.</p>", 404
    
    if enlaces[token].get("used", True):
        return "<h1>This link has been already used</h1><p>This link is not valid anymore.</p>", 404
    
    friend = enlaces[token]["friend"]
    participant = enlaces[token]["participant"]
    
    enlaces[token]["used"] = True
    try:
        with open("friends_secret.json", "w") as file:
            json.dump(enlaces, file, indent=4)
    except IOError:
        return "<h1>Error saving status</h1><p>Cannot update assignations file.</p>", 500
    
    return render_template("revelation.html", secret_friend=friend, participant=participant)


@app.route("/get_info", methods=["GET"])
def get_info():
    with open("friends_secret.json", "r") as file:
        enlaces = json.load(file)
        all_info=[]
        for key, values in enlaces.items():
            new_dict={}
            token_key=key
            participant=values.get('participant')
            used=values.get('used')
            new_dict[participant]={f"{URL}/reveal?token={token_key}": 'used' if used else 'not used'  }
            all_info.append(new_dict)
    return {'all':all_info}


@app.route("/disable_all", methods=["GET"])
def disable_all():
    with open("friends_secret.json", "r") as file:
        enlaces = json.load(file)

    for token in enlaces:
        enlaces[token]["used"] = True

    with open("friends_secret.json", "w") as file:
        json.dump(enlaces, file, indent=4)

    return{"info":"All tokens were been disabled"}


@app.route("/activate_all", methods=["GET"])
def activate_all():
    with open("friends_secret.json", "r") as file:
        enlaces = json.load(file) 

    for token in enlaces:
        enlaces[token]["used"] = False

    with open("friends_secret.json", "w") as file:
        json.dump(enlaces, file, indent=4)

    return{"info":"All tokens were been activated"}


if __name__ == "__main__":
    app.run(debug=True)

