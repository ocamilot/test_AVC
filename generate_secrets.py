import json

# Definir los nuevos valores de los secretos
secrets = {
    "SECRET_ONE": "PRUEBALO",
    "SECRET_TWO": "nuevo_valor_2"
}

# Guardar los secretos en un archivo JSON
with open("secrets.json", "w") as f:
    json.dump(secrets, f)

print("✅ Archivo 'secrets.json' generado correctamente.")
