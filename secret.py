from cryptography.fernet import Fernet

# Función para cargar la clave de encriptación
def load_key():
    """
    Carga la clave de encriptación desde un archivo.
    """
    return open("secret.key", "rb").read()

# Función para encriptar datos
def encrypt_data(data):
    """
    Encripta una cadena de texto.
    """
    key = load_key()
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode())
    return encrypted_data

# Datos del usuario
username = "Ñañito"
password = "PolloFrito"

# Encriptamos la contraseña
encrypted_password = encrypt_data(password)

# Mostramos la contraseña encriptada y el nombre de usuario
print(f"Usuario: {username}, Contraseña encriptada: {encrypted_password.decode()}")

# Guardamos el usuario y la contraseña encriptada en un archivo CSV
import csv

with open('users.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['username', 'password'])
    writer.writerow([username, encrypted_password.decode()])
