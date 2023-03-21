from .config import settings
from fastapi_keycloak import FastAPIKeycloak

def config_keycloak():

    return FastAPIKeycloak(
        server_url=settings["KEYCLOAK_SERVER_URL"],
        client_id=settings["KEYCLOAK_CLIENT_ID"],
        client_secret=settings["KEYCLOAK_CLIENT_SECRET"],
        admin_client_secret=settings["KEYCLOAK_ADMIN_CLIENT_SECRET"],
        realm=settings["KEYCLOAK_REALM"],
        callback_uri=settings["KEYCLOAK_CALLBACK_URI"],
    )