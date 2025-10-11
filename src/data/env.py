import os
import dotenv


class Env:
    def __init__(self):
        dotenv.load_dotenv()


    def __get_var(self, var_name: str) -> str:
        env: str | None = os.getenv(var_name)
        if env is None:
            raise ValueError(f"Environment variable '{var_name}' is not set.")
        return env


    def get_client_id(self) -> str:
        return self.__get_var("CLIENT_ID")


    def get_client_secret(self) -> str:
        return self.__get_var("CLIENT_SECRET")


    def get_redirect_uri(self) -> str:
        return self.__get_var("REDIRECT_URI")


    def get_api_key(self) -> str:
        return self.__get_var("API_KEY")
