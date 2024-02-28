import csv
import base64
from cryptography.fernet import Fernet

# Función para cargar la clave de encriptación desde el archivo
def load_key():
    return open("secret.key", "rb").read()

# Función para desencriptar los datos

def decrypt_data(encrypted_data):
    key = load_key()
    f = Fernet(key)
    decrypted_data = f.decrypt(encrypted_data)  # encrypted_data debería ser bytes aquí
    return decrypted_data.decode('utf-8')  # Convierte los bytes desencriptados a string UTF-8


# Función para leer, desencriptar los datos de la encuesta desde el archivo CSV y guardarlos en un nuevo archivo

def decrypt_survey_data(input_filename, output_filename):
    with open(input_filename, 'r') as file, open(output_filename, 'w', newline='', encoding='utf-8') as outfile:
        csv_reader = csv.reader(file)
        csv_writer = csv.writer(outfile)
        for row in csv_reader:
            encrypted_data_b64 = row[0]
            encrypted_data = base64.b64decode(encrypted_data_b64)
            decrypted_data = decrypt_data(encrypted_data)
            csv_writer.writerow([decrypted_data])


# Uso de la función
if __name__ == "__main__":
    decrypt_survey_data('encrypted_survey_data.csv', 'decrypted_survey_data.csv')
