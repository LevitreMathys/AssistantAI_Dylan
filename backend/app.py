from fastapi import FastAPI

class App(FastAPI):

    def __init__(self) -> None:
        super().__init__()

    

    def root(self) -> dict:
        return {"message": "Bienvenue sur l'API Louis"}