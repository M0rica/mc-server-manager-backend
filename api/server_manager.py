import os
import json
import random
import shutil
import subprocess
from datetime import datetime
from threading import Thread

import requests
from bs4 import BeautifulSoup

from config import get_config
from api.minecraft_server import MinecraftServer


class ServerManager:
    def __init__(self):

        self.base_path: str
        self.servers_path: str
        self.build_path: str # directory buildtools is in and where new versions will be build
        self.build_tools_path: str
        self.install_proc: subprocess.Popen = None
        self.install_logs = ""

        self.available_versions = {}
        self._servers = {}

        self.load_config()
        self.load_servers()
        self._get_available_minecraft_versions()

    def load_config(self):
        config = get_config()["servers"]

        self.base_path = config["path"]
        self.servers_path = os.path.join(self.base_path, "servers")

    def load_servers(self):
        file_location = os.path.join(self.base_path, "servers.json")
        if os.path.isfile(file_location):
            with open(file_location, "w") as f:
                data = json.load(f)

    def save_servers(self):
        server_data = [{id, dict(server)} for id, server in self._servers]
        save = {
            "servers": server_data
        }
        with open(os.path.join(self.servers_path, "servers.json"), "r") as f:
            json.dump(save, f)

    def server_exists(self, server_id: int) -> bool:
        return server_id in self._servers

    def _get_server(self, server_id: int) -> MinecraftServer:
        server = self._servers.get(server_id)
        if server is not None:
            server.update()
        return server

    def _get_available_minecraft_versions(self):
        def get_webpage(url):
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:96.0) Gecko/20100101 Firefox/96.0"
            }
            return requests.get(url, headers=headers).text

        webpage = get_webpage("https://mcversions.net")
        soup = BeautifulSoup(webpage, "html.parser")
        releases = soup.find_all("div",
                                 {"class": "item flex items-center p-3 border-b border-gray-700 snap-start ncItem"})
        for version in releases:
            self.available_versions[version.get("id")] = "https://mcversions.net" + version.find("a", text="Download").get("href")

    def create_server(self, data: dict) -> int:
        id = 0
        while id != 0 and id not in self._servers:
            id = random.randint(1000, 9999)
        thrd = Thread(target=self._create_server, args=[id, data])
        thrd.start()
        return id

    def _create_server(self, id: int, data: dict):
        server_path = os.path.join(self.servers_path, str(id))
        if os.path.exists(server_path):
            shutil.rmtree(server_path)
        os.makedirs(server_path)
        path_data = {
            "path": server_path,
            "jar": f"{data['type']}.jar"
        }
        """if data["type"] in ["spigot", "craftbukkit"]:
            build_path = self._bukkit_creator.create_server(data)
            shutil.copy(build_path,
                        os.path.join(server_path, f"{data['type']}.jar"))"""
        self._servers[id] = MinecraftServer(id, data["name"], datetime.now(), path_data)
        return id

    def get_server_status(self, server_id: int) -> dict:
        status = {
            "status": self._get_server(server_id).get_status()
        }
        return status

    def get_server_data(self, server_id: int) -> dict:
        server = self._get_server(server_id)
        if server is not None:
            return server.compile_data()