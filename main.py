from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="files/static"), name="static")


@app.get("/")
async def home():
    return FileResponse(
        "build/index.html", 200
    )


@app.get("/api/get_info")
async def get_infos():
    return JSONResponse(
        dict(
            x=5,
            y=3,
            z=42,
            a=420
        ),
        headers={"Access-Control-Allow-Origin": "*"}
    )
