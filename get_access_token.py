import os
import requests

# Leer variables de entorno desde GitHub Secrets
client_id = os.getenv("AVC_CLIENT_ID")
client_secret = os.getenv("AVC_SECRET")
directorio_actual = os.getcwd()
print("Directorio actual:", directorio_actual)
print("Cliente ID:", client_id)
print("Secret:", client_secret)


if not client_id or not client_secret:
    raise ValueError("Las variables de entorno AVC_CLIENT_ID y AVC_SECRET deben estar configuradas.")

# URL de la API de Amazon
url = "https://api.amazon.com/auth/o2/token"

params = {
    "grant_type": "client_credentials",
    "scope": "sellingpartnerapi::client_credential:rotation",
    "client_id": client_id,
    "client_secret": client_secret
}

headers = {"Content-Type": "application/x-www-form-urlencoded"}

# Realizar la solicitud
response = requests.post(url, data=params, headers=headers)

# Manejo de la respuesta
if response.status_code == 200:
    access_token = response.json().get("access_token", "No access token found")
    print("Access Token:", access_token)
else:
    print("Error:", response.status_code, response.text)
