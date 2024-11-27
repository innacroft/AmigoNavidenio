import random
import string
import json

from flask import Flask, render_template, request


# Crear una aplicación Flask
app = Flask(__name__)

# Lista de nombres de los participantes
participantes = ["Ingrid", "Julian", "Yuly", "Andres", "Esteban", "Lina", "Lino", "Yudy"]


def asignar_amigo_secreto(participantes):
    amigos = participantes[:]
    random.shuffle(amigos)
    
    while any(p == a for p, a in zip(participantes, amigos)):
        random.shuffle(amigos)
    
    return dict(zip(participantes, amigos))

# Crear los enlaces personalizados
def crear_enlaces(asignaciones):
    base_url = "https://innacroft.pythonanywhere.com"
    enlaces = {}
    enlaces_show = {}
    
    for participante, amigo in asignaciones.items():
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=8))  # Generar un token único
        link = f"{base_url}/reveal?token={token}"
        enlaces[token] = {"participante": participante, "amigo": amigo, "usado": False}
        enlaces_show[participante] = f"Entra aqui para revelar tu amigo navideño: {link}"
        # Guardar las asignaciones y los enlaces en un archivo JSON para referencia
    with open("amigos_secreto.json", "w") as file:
        json.dump(enlaces, file, indent=4)
    return enlaces_show

# Función para asignar amigos secretos
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
    
    # Cargar las asignaciones desde el archivo JSON
    try:
        with open("amigos_secreto.json", "r") as file:
            enlaces = json.load(file)
    except FileNotFoundError:
        return "<h1>Error al cargar el archivo de asignaciones</h1><p>No se ha encontrado el archivo de amigos secretos.</p>", 500
    
    # Verificar si el token es válido
    if token not in enlaces:
        return "<h1>Enlace inválido</h1><p>El token proporcionado no es válido.</p>", 404
    
    # Verificar si el enlace ya ha sido usado
    if enlaces[token].get("usado", False):
        return "<h1>Este enlace ya ha sido usado.</h1><p>El enlace ya no es válido.</p>", 404
    
    # Si el token es válido y no se ha usado, obtenemos el amigo secreto
    amigo = enlaces[token]["amigo"]
    participante = enlaces[token]["participante"]
    
    # Marcar el enlace como usado
    enlaces[token]["usado"] = True
    # Guardar los cambios en el archivo
    try:
        with open("amigos_secreto.json", "w") as file:
            json.dump(enlaces, file, indent=4)
    except IOError:
        return "<h1>Error al guardar el estado</h1><p>No se pudo actualizar el archivo de asignaciones.</p>", 500
    
    # Renderizar la página con el amigo secreto
    return render_template("revelacion.html", amigo_secreto=amigo, participante=participante)


# Iniciar el servidor
if __name__ == "__main__":
    app.run(debug=True)

