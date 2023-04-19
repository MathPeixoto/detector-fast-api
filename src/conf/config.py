from dotenv import load_dotenv
import os

load_dotenv()

settings = {
    "COGNITO_POOL_URL": os.getenv("COGNITO_POOL_URL"),
    "APP_CLIENT_ID": os.getenv("APP_CLIENT_ID"),
}

#
# import os
# import hashlib
# import hmac
# import boto3
# from dotenv import load_dotenv
# import base64
#
# load_dotenv()
#
# def get_secret_hash(username, client_id, client_secret):
#     msg = username + client_id
#     dig = hmac.new(client_secret.encode("utf-8"), msg=msg.encode("utf-8"), digestmod=hashlib.sha256).digest()
#     return base64.b64encode(dig).decode()
#
# def get_tokens(username, password, client_id, client_secret, region="your_aws_region"):
#     secret_hash = get_secret_hash(username, client_id, client_secret)
#
#     client = boto3.client("cognito-idp", region_name=region)
#
#     response = client.initiate_auth(
#         AuthFlow="USER_PASSWORD_AUTH",
#         AuthParameters={
#             "USERNAME": username,
#             "PASSWORD": password,
#             "SECRET_HASH": secret_hash
#         },
#         ClientId=client_id
#     )
#
#     return response["AuthenticationResult"]
#
# username = "matheus.pires.rj@gmail.com"
# password = "Rh4d4ss@"
#
# client_id = "1tvqm68dm9v03kchmg75mip9ji"
# client_secret = "19jqcnonrt83c5p748ecdf2t358r0tf74afhd7qs767pm7p5d1fr"
# region = "us-east-1"
#
# tokens = get_tokens(username, password, client_id, client_secret, region)
#
# if __name__ == "__main__":
#     print(tokens["IdToken"])