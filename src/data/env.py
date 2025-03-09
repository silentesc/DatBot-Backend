import os
import dotenv


class Env:
    def __init__(self):
        dotenv.load_dotenv()


    def get_client_id(self):
        return os.getenv("CLIENT_ID")


    def get_client_secret(self):
        return os.getenv("CLIENT_SECRET")


    def get_redirect_uri(self):
        return os.getenv("REDIRECT_URI")
