import json
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime
from json.decoder import JSONDecodeError
from typing import Dict

import requests
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from paths import data_path

router = APIRouter(
    prefix="/api/files",
    responses={404: {"description": "Not found"}},
)

jar_path = os.path.join(data_path, "jars")
build_tools_path = os.path.join(jar_path, "BuildTools.jar")

logs = ""
proc: subprocess.Popen


@dataclass
class File:
    path: str
    created_at: datetime

    def __dict__(self):
        return dict(
            path=self.path,
            created_at=self.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f")
        )

    @classmethod
    def from_json(cls, json_obj):
        return cls(
            path=json_obj["path"],
            created_at=datetime.strptime(json_obj.get("created_at", ""), '%Y-%m-%dT%H:%M:%S.%f')
        )


_data: Dict[str, File]

if os.path.exists(path := os.path.join(jar_path, "files.json")):
    try:
        tmp = json.load(open(path))
        _data = {key: File.from_json(value) for key, value in tmp.items()}
    except JSONDecodeError:
        _data = {}
else:
    _data = {}


@router.get("/status")
def status():
    return JSONResponse({key: value.__dict__() for key, value in _data.items()}, 200)


@router.get("/download/{file}")
def download(file: str):
    if not os.path.exists(build_tools_path):
        return JSONResponse(dict(error="No BuildTools"), 500)
    global logs, proc
    logs = f"Starting installation of {file}"
    proc = subprocess.Popen(["java", "-jar", build_tools_path, "--rev", file], stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    print("Process started")
    return JSONResponse(dict(info="Started Process"), 200)


@router.get("/download/progress")
def progress():
    global logs
    logs += proc.communicate()
    if logs:
        return JSONResponse(dict(logs=logs))
    else:
        return JSONResponse(dict(logs="", error="No active download"))


@router.post("/download")
def download_build_tools():
    created = False
    if not os.path.exists(build_tools_path):
        resp = requests.get(
            "https://hub.spigotmc.org/jenkins/job/BuildTools/lastSuccessfulBuild/artifact/target/BuildTools.jar")

        with open(build_tools_path, "wb") as f:
            f.write(resp.content)
            created = True

    _data["build_tools"] = File(
        path=build_tools_path,
        created_at=datetime.now()
    )
    save_file()

    return JSONResponse(dict(
        new_created=created
    ), 200)


def save_file():
    json.dump({key: value.__dict__() for key, value in _data.items()},
              open(os.path.join(jar_path, "files.jar"), "w"))
