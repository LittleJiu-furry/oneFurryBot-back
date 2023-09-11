from fastapi import APIRouter,FastAPI,Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

class uiServer():
    def __init__(self):
        self.app = FastAPI()
        self.app.mount("/static", StaticFiles(directory="static"), name="static")
        api = APIRouter()
        # 主界面
        api.add_api_route("/",self.index,methods=["GET"],response_class=HTMLResponse)
        api.add_api_route("/index",self.index,methods=["GET"],response_class=HTMLResponse)
        api.add_api_route("/index.html",self.index,methods=["GET"],response_class=HTMLResponse)
        
        self.app.include_router(api)

    async def runUI(self,port:int):
        conf = uvicorn.Config(
            app=self.app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
        self.uiserver = uvicorn.Server(conf)
        await self.uiserver.serve()
    
    async def close(self):
        await self.uiserver.shutdown()



    
    async def index(self):
        pass