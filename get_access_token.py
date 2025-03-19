import os
import requests
import json
import boto3

# Leer variables de entorno desde GitHub Secrets
client_id = os.getenv("AVC_CLIENT_ID")
client_secret = os.getenv("AVC_SECRET")
sqs_queue_url = "https://sqs.eu-west-1.amazonaws.com/211125721469/AVC_API_SECRET_ROTATION"

# Validar que las variables de entorno estén configuradas
if not client_id or not client_secret:
    raise ValueError("Las variables de entorno AVC_CLIENT_ID y AVC_SECRET deben estar configuradas.")

# Obtener el directorio actual
directorio_actual = os.getcwd()
print("Directorio actual:", directorio_actual)
print("Cliente ID:", client_id)

# Paso 1: Obtener LWA Access Token
url = "https://api.amazon.com/auth/o2/token"
params = {
    "grant_type": "client_credentials",
    "scope": "sellingpartnerapi::client_credential:rotation",
    "client_id": client_id,
    "client_secret": client_secret
}
headers = {"Content-Type": "application/x-www-form-urlencoded"}

response = requests.post(url, data=params, headers=headers)

if response.status_code == 200:
    access_token = response.json().get("access_token")
    print("Access Token obtenido correctamente.")
else:
    print("Error al obtener el Access Token:", response.status_code, response.text)
    exit(1)

# Paso 2: Usar el Access Token para rotar el secreto
rotate_url = "https://sellingpartnerapi-na.amazon.com/applications/2023-11-30/clientSecret"
rotate_headers = {
    "Content-Type": "application/json",
    "x-amz-access-token": access_token
}

rotate_response = requests.post(rotate_url, headers=rotate_headers)

if rotate_response.status_code == 204:
    print("✅ Secreto rotado exitosamente.")
else:
    print("❌ Error al rotar el secreto:", rotate_response.status_code, rotate_response.text)
    exit(1)

# Paso 3: Leer el nuevo secreto de SQS
sqs = boto3.client("sqs", region_name="eu-west-1")

def get_new_client_secret():
    response = sqs.receive_message(
        QueueUrl=sqs_queue_url,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=10
    )

    if "Messages" in response:
        message = response["Messages"][0]
        body = json.loads(message["Body"])  # Convertir el mensaje a JSON

        # Extraer `clientId` y `newClientSecret`
        received_client_id = body["payload"]["applicationOAuthClientNewSecret"]["clientId"]
        new_client_secret = body["payload"]["applicationOAuthClientNewSecret"]["newClientSecret"]

        # Validar si el clientId coincide con el esperado
        if received_client_id == client_id:
            print(f"✅ Nuevo Client Secret recibido: {new_client_secret}")

            # Borrar el mensaje de la cola para evitar reprocesarlo
            receipt_handle = message["ReceiptHandle"]
            sqs.delete_message(QueueUrl=sqs_queue_url, ReceiptHandle=receipt_handle)
            print("✅ Mensaje eliminado de la cola SQS.")

            return new_client_secret
        else:
            print("❌ El clientId recibido no coincide con el esperado.")
            return None
    else:
        print("❌ No hay mensajes en la cola SQS.")
        return None

# Ejecutar la función para obtener el nuevo secreto
new_secret = get_new_client_secret()
print("FINALMENTE EL SECRETO ES: " + new_secret)

if new_secret:
    print("🔑 Nuevo secreto obtenido correctamente.")
else:
    print("⚠️ No se pudo obtener el nuevo secreto.")
