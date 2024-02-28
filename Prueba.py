import streamlit as st
from cryptography.fernet import Fernet
import pandas as pd
import csv
from datetime import datetime
import base64

# Función para cargar la clave de encriptación
def load_key():
    return open("secret.key", "rb").read()


# Función para verificar las credenciales del usuario
def verify_login(username, password):
    users_df = pd.read_csv('users.csv', encoding='latin-1')
    user = users_df[users_df['username'] == username]
    if not user.empty:
        stored_password_encrypted = user['password'].values[0]
        stored_password = decrypt_data(stored_password_encrypted)
        if password == stored_password:
            return True
    return False

# Asegúrate de tener la función para cargar la clave de encriptación
def load_key():
    return open("secret.key", "rb").read()

# Aquí está la función encrypt_data
def encrypt_data(data):
    key = load_key()
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode('utf-8'))
    return encrypted_data


# Funcion desencriptar datos 
def decrypt_data(encrypted_data):
    key = load_key()
    f = Fernet(key)
    decrypted_data = f.decrypt(encrypted_data)  # Elimina .encode('utf-8')
    return decrypted_data.decode('utf-8')



def login_system():
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        st.title('Sistema de Login')

        username = st.text_input('Nombre de Usuario', key='login_username')
        password = st.text_input('Contraseña', type='password', key='login_password')

        if st.button('Login'):
            if verify_login(username, password):
                st.success('Login exitoso')
                st.session_state['logged_in'] = True
                st.session_state['logged_in_user'] = username
            else:
                st.error('Nombre de usuario o contraseña incorrectos')

def request_event_name():
    # Asegúrate de que esta función solo se llame si el usuario está logueado.
    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        event_name_input = st.text_input('Nombre del Evento o Reunión', key='event_name_input')
        submit_event = st.button('Confirmar Evento', key='submit_event')
        if submit_event:
            st.session_state['event_name'] = event_name_input
            # Aquí podrías redirigir al usuario a la encuesta o realizar otra acción.

                
                
def save_survey_data(user, event_name, apellido, nombre, municipio, celular, correo, acepta_politica, fecha_nacimiento):
    # Concatenamos la información en una sola cadena de texto, incluyendo el nombre del evento
    data_str = f"{user},{event_name},{apellido},{nombre},{municipio},{celular},{correo},{acepta_politica},{fecha_nacimiento}"
    # Encriptamos los datos
    encrypted_data = encrypt_data(data_str)
    # Codificamos los datos encriptados a Base64 para guardarlos como una cadena
    b64_encoded_data = base64.b64encode(encrypted_data).decode('utf-8')
    
    # Guardamos los datos codificados en Base64 en un archivo CSV
    with open('encrypted_survey_data.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([b64_encoded_data])

import streamlit as st
import pandas as pd
from datetime import datetime

# Cargar los municipios desde el archivo CSV
def load_municipios():
    municipios_df = pd.read_csv('municipios.csv', header=None)  # Asume que tu CSV no tiene encabezado
    return municipios_df[0].tolist()  # Convierte la columna de municipios en una lista

def show_survey():
    st.title('Encuesta')
    
    # Recupera el nombre del usuario y el evento de la sesión
    user = st.session_state.get('logged_in_user', 'Anónimo')
    event_name = st.session_state.get('event_name', 'Evento Desconocido')

    # Crea los widgets de la encuesta
    apellido = st.text_input('Apellidos')
    nombre = st.text_input('Nombres')
    municipio = st.selectbox('Municipio', load_municipios())
    celular = st.text_input('Celular')
    correo = st.text_input('Correo Electrónico')
    acepta_politica = st.checkbox('Acepto la política y tratamiento de datos')
    fecha_nacimiento = st.date_input('Fecha de Nacimiento', min_value=datetime(1900, 1, 1), max_value=datetime.now())

    if st.button('Enviar Encuesta'):
        # Guarda los datos de la encuesta
        save_survey_data(user, event_name, apellido, nombre, municipio, celular, correo, acepta_politica, fecha_nacimiento)
        
        # Actualiza el estado con la última persona encuestada
        st.session_state['last_surveyed'] = f"{nombre} {apellido}"
        
        # Muestra un mensaje de éxito que incluye el nombre de la persona
        st.success(f'¡Encuesta enviada exitosamente por {nombre} {apellido}!')

    # Muestra el nombre y apellido de la última persona encuestada
    if 'last_surveyed' in st.session_state:
        st.write(f"Última persona encuestada: {st.session_state['last_surveyed']}")



if __name__ == "__main__":
    login_system()
    request_event_name()  # Llama a la función después de login_system para asegurar orden correcto.
    if 'logged_in' in st.session_state and st.session_state['logged_in'] and 'event_name' in st.session_state:
        show_survey()  # Asegúrate de que la encuesta se muestra solo después de que se ha definido el evento.
