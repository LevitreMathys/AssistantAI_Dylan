from fastapi import FastAPI
from backend.router.messages import MessagesRouter
from backend.router.root import RootRouter
from app.LouisApp import LouisApp
class App(FastAPI):

    def __init__(self) -> None:
        super().__init__()
        self.Louis = LouisApp()
        self._include_routers()

    def _include_routers(self) -> None:
        self.include_router(RootRouter())
        self.include_router(MessagesRouter(self.Louis))