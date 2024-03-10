import streamlit as st
from cryptography.fernet import Fernet
import pandas as pd
import csv
from datetime import datetime
import base64
import boto3
from botocore.exceptions import NoCredentialsError
import io

# Usa st.columns para colocar el logo junto al título
col1, col2 = st.columns([1, 4])  # Ajusta las proporciones según necesites

with col1:  # En esta columna mostramos el logo
    st.image('argo.jpg', width=100)  # Ajusta el tamaño según sea necesario

with col2:  # En esta columna mostramos el texto
    st.markdown("## Sistema de Registro ARGO - Subsecretaria de Innovación", unsafe_allow_html=True)



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

def load_sexo():
    sexos_df = pd.read_csv('sexo.csv', header=None)
    return sexos_df[0].tolist()                
                
# Ajustaremos la función save_survey_data para incluir el sexo en los datos guardados.
def save_survey_data(user, event_name, apellido, nombre, sexo, municipio, celular, correo, acepta_politica, fecha_nacimiento, causa_conflicto, contribucion_paz):
    # Convertimos la información de la encuesta en una sola fila de un DataFrame
    data_dict = {
        'user': [user],
        'event_name': [event_name],
        'apellido': [apellido],
        'nombre': [nombre],
        'sexo': [sexo],
        'municipio': [municipio],
        'celular': [celular],
        'correo': [correo],
        'acepta_politica': [acepta_politica],
        'fecha_nacimiento': [fecha_nacimiento],
        'causa_conflicto': [causa_conflicto],
        'contribucion_paz': [contribucion_paz]
    }
    new_data_df = pd.DataFrame(data_dict)
    
    # Configura el nombre del bucket y la clave del objeto S3
    bucket_name = 'encuesta'
    s3_file_key = 'encuestas/survey_data.csv'
    
    # Crea el cliente S3
    s3_client = boto3.client('s3', aws_access_key_id='AKIATCKARMOACZXT5P3V', aws_secret_access_key='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', region_name='us-east-2')

    # Intenta descargar el archivo CSV existente desde S3
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=s3_file_key)
        # Lee el contenido del archivo en un DataFrame
        existing_data = pd.read_csv(io.BytesIO(response['Body'].read()), encoding='utf-8')
        # Añade la nueva fila
        updated_data = pd.concat([existing_data, new_data_df], ignore_index=True)
    except s3_client.exceptions.NoSuchKey:
        # El archivo no existe, crea un nuevo DataFrame
        updated_data = new_data_df

    # Convierte el DataFrame actualizado a un CSV
    csv_buffer = io.StringIO()
    updated_data.to_csv(csv_buffer, index=False)

    # Sube el CSV actualizado de nuevo a S3
    s3_client.put_object(Bucket=bucket_name, Key=s3_file_key, Body=csv_buffer.getvalue())

import streamlit as st
import pandas as pd
from datetime import datetime

# Cargar los municipios desde el archivo CSV
def load_municipios():
    municipios_df = pd.read_csv('municipios.csv', header=None)  # Asume que tu CSV no tiene encabezado
    return municipios_df[0].tolist()  # Convierte la columna de municipios en una lista

def show_survey():
    st.title('Registro de Eventos Subsecretaria de Innovación')
    
    # Recupera el nombre del usuario y el evento de la sesión
    user = st.session_state.get('logged_in_user', 'Anónimo')
    event_name = st.session_state.get('event_name', 'Evento Desconocido')

    # Crea los widgets de la encuesta
    apellido = st.text_input('¿Cuales son sus apellidos?')
    nombre = st.text_input('¿Cuales son sus nombres?')
    municipio = st.selectbox('¿En que Municipio vive?', load_municipios())
    celular = st.text_input('¿Cual es su numero de celular?')
    sexo = st.selectbox('¿Con que genero se identifica?', load_sexo())
    correo = st.text_input('¿Cual es su correo Electrónico?')
    causa_conflicto = st.text_area("En su opinión, ¿cuáles son las principales causas del conflicto y la violencia en la región?")
    contribucion_paz = st.text_area("¿De qué manera cree que podría contribuir personalmente a la construcción de paz en su territorio? Por favor, considere propuestas específicas o proyectos en los que podría participar o iniciar.")
    acepta_politica = st.checkbox('¿Acepta la política y tratamiento de datos?')
    fecha_nacimiento = st.number_input('¿Cual es su año de nacimiento?', min_value=1900, max_value=datetime.now().year, format='%d')

    if st.button('Enviar Encuesta'):
        # Guarda los datos de la encuesta
        save_survey_data(user, event_name, apellido, nombre, sexo, municipio, celular, correo, acepta_politica, fecha_nacimiento, causa_conflicto, contribucion_paz)
        
        
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
