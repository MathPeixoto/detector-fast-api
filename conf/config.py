from dotenv import load_dotenv
import os

load_dotenv()

settings = {
    "KEYCLOAK_SERVER_URL": os.getenv("KEYCLOAK_SERVER_URL"),
    "KEYCLOAK_CLIENT_ID": os.getenv("KEYCLOAK_CLIENT_ID"),
    "KEYCLOAK_CLIENT_SECRET": os.getenv("KEYCLOAK_CLIENT_SECRET"),
    "KEYCLOAK_ADMIN_CLIENT_SECRET": os.getenv("KEYCLOAK_ADMIN_CLIENT_SECRET"),
    "KEYCLOAK_REALM": os.getenv("KEYCLOAK_REALM"),
    "KEYCLOAK_CALLBACK_URI": os.getenv("KEYCLOAK_CALLBACK_URI"),
}
