import webbrowser

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

import uvicorn
from fastapi_utils.tasks import repeat_every
from starlette.staticfiles import StaticFiles
from config import load_config
load_config()

from api import api

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(api.router)
app.include_router(api.server_router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return FileResponse(
        "static/index.html",
        200
    )


if __name__ == '__main__':
    #webbrowser.open('localhost:5000')
    uvicorn.run("main:app", host="0.0.0.0", workers=2, port=5000, reload=True)

