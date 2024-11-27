import random
import string
import json

from flask import Flask, jsonify, render_template, request


app = Flask(__name__)
URL = "https://innacroft.pythonanywhere.com"
participantes = ["Ingrid", "Julian", "Yuly", "Andres", "Esteban", "Lina", "Lino", "Yudy"]

@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if request.method == 'POST':
        participantes = request.form.get('participantes')

        if not participantes:
            return jsonify({"error": "No se enviaron participantes."}), 400

        participantes = [p.strip() for p in participantes.split(',') if p.strip()]

        asignaciones = asignar_amigo_secreto(participantes)
        enlaces_personalizados = crear_enlaces(asignaciones)
        return enlaces_personalizados

    return '''
        <form method="post">
        <label for="participantes">Participantes (separados por comas):</label><br>
        <textarea name="participantes" rows="4" cols="50"></textarea><br>
        <button type="submit">Asignar automáticamente</button>
    </form>
    '''

def asignar_amigo_secreto(participantes):
    amigos = participantes[:]
    random.shuffle(amigos)
    
    while any(p == a for p, a in zip(participantes, amigos)):
        random.shuffle(amigos)
    
    return dict(zip(participantes, amigos))

def crear_enlaces(asignaciones):
    
    enlaces = {}
    enlaces_show = {}
    
    for participante, amigo in asignaciones.items():
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=8))  # Generar un token único
        link = f"{URL}/reveal?token={token}"
        enlaces[token] = {"participante": participante, "amigo": amigo, "usado": False}
        enlaces_show[participante] = f"Entra aqui para revelar tu amigo navideño: {link}"
    with open("amigos_secreto.json", "w") as file:
        json.dump(enlaces, file, indent=4)
    return enlaces_show

@app.route("/assign", methods=["GET"])
def assign():
    asignaciones = asignar_amigo_secreto(participantes)
    enlaces_personalizados = crear_enlaces(asignaciones)
    print(enlaces_personalizados)
    return enlaces_personalizados



# Ruta para revelar el amigo secreto
@app.route("/reveal", methods=["GET"])
def reveal():
    token = request.args.get("token")
    
    if not token:
        return "<h1>Token no proporcionado</h1><p>Por favor, asegúrate de tener un enlace válido.</p>", 400
    
    try:
        with open("amigos_secreto.json", "r") as file:
            enlaces = json.load(file)
    except FileNotFoundError:
        return "<h1>Error al cargar el archivo de asignaciones</h1><p>No se ha encontrado el archivo de amigos secretos.</p>", 500
    
    if token not in enlaces:
        return "<h1>Enlace inválido</h1><p>El token proporcionado no es válido.</p>", 404
    
    if enlaces[token].get("usado", True):
        return "<h1>Este enlace ya ha sido usado.</h1><p>El enlace ya no es válido.</p>", 404
    
    amigo = enlaces[token]["amigo"]
    participante = enlaces[token]["participante"]
    
    enlaces[token]["usado"] = True
    try:
        with open("amigos_secreto.json", "w") as file:
            json.dump(enlaces, file, indent=4)
    except IOError:
        return "<h1>Error al guardar el estado</h1><p>No se pudo actualizar el archivo de asignaciones.</p>", 500
    
    return render_template("revelacion.html", amigo_secreto=amigo, participante=participante)


@app.route("/get_info", methods=["GET"])
def get_info():
    with open("amigos_secreto.json", "r") as file:
        enlaces = json.load(file)
        all_info=[]
        for key, values in enlaces.items():
            new_dict={}
            token_key=key
            participante=values.get('participante')
            usado=values.get('usado')
            new_dict[participante]={f"{URL}/reveal?token={token_key}": 'usado' if usado else 'sin usar'  }
            all_info.append(new_dict)
    return {'all':all_info}


@app.route("/disable_all", methods=["GET"])
def disable_all():
    with open("amigos_secreto.json", "r") as file:
        enlaces = json.load(file)

    for token in enlaces:
        enlaces[token]["usado"] = True

    with open("amigos_secreto.json", "w") as file:
        json.dump(enlaces, file, indent=4)

    return{"info":"Todos los tokens han sido deshabilitados."}


@app.route("/activate_all", methods=["GET"])
def activate_all():
    with open("amigos_secreto.json", "r") as file:
        enlaces = json.load(file) 

    for token in enlaces:
        enlaces[token]["usado"] = False

    with open("amigos_secreto.json", "w") as file:
        json.dump(enlaces, file, indent=4)

    return{"info":"Todos los tokens han sido activados."}


if __name__ == "__main__":
    app.run(debug=True)

