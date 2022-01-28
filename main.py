import webbrowser

from fastapi import FastAPI
from fastapi.responses import FileResponse

import uvicorn
from starlette.staticfiles import StaticFiles

from api import server_routing

from api import api

app = FastAPI()

app.include_router(api.router)
app.include_router(server_routing.router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return FileResponse(
        "static/index.html",
        200
    )


if __name__ == '__main__':
    webbrowser.open('localhost:5000')
    uvicorn.run("main:app", host="0.0.0.0", workers=2, port=5000, reload=True)

