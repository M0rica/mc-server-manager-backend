from datetime import datetime
import json
import os
import random
import shutil
import subprocess
import time

import requests

from config import get_config
from api.minecraft_server import MinecraftServer

class BukkitManager:

    def __init__(self):

        self.base_path: str
        self.servers_path: str
        self.build_path: str # directory buildtools is in and where new versions will be build
        self.build_tools_path: str
        self.build_proc: subprocess.Popen = None
        self.install_logs = ""

        self.available_versions = []
        self._servers = {}

        self.load_config()
        self.load_servers()

    def load_config(self):
        config = get_config()["bukkit"]

        self.base_path = config["path"]
        self.servers_path = os.path.join(self.base_path, "servers")
        self.build_path = os.path.join(self.base_path, "build")
        self.build_tools_path = os.path.join(self.build_path, "BuildTools.jar")

    def load_servers(self):
        with open(os.path.join(self.servers_path, "servers.json"), "w") as f:
            data = json.load(f)


    def save_servers(self):
        server_data = [{id, dict(server)} for id, server in self._servers]
        save = {
            "servers": self._servers
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

    def download_buildtools(self, force_reinstall: bool = False):
        if os.path.exists(self.build_path):
            if force_reinstall:
                shutil.rmtree(self.build_path)
            else:
                return
        os.mkdir(self.build_path)
        resp = requests.get(
            "https://hub.spigotmc.org/jenkins/job/BuildTools/lastSuccessfulBuild/artifact/target/BuildTools.jar")
        with open(self.build_tools_path, "wb") as f:
            f.write(resp.content)

    def build_server(self, version: str, craftbukkit: bool = False):
        if not os.path.exists(self.build_tools_path):
            self.install_logs += "\nDownloading BuildTools..."
            self.download_buildtools()
        if self.build_proc is None:
            command = ["java", "-jar", self.build_tools_path, "--rev", version]
            if craftbukkit:
                command += ["--compile", "craftbukkit"]
            self.build_proc = subprocess.Popen(command,
                                               stdin=subprocess.PIPE,
                                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.install_logs = ""
        while self.build_proc.poll() is None:
            time.sleep(1)

    def create_server(self, data: dict):
        self.build_server(data["version"], data["type"] == "craftbukkit")
        id = 0
        while id != 0 and id not in self._servers:
            id = random.randint(1000, 9999)
        server_path = os.path.join(self.servers_path, str(id))
        if os.path.exists(server_path):
            shutil.rmtree(server_path)
        os.mkdir(server_path)
        path_data = {
            "path": server_path,
            "jar": f"{data['type']}.jar"
        }
        shutil.copy(os.path.join(self.build_path, f"{data['type']}-{data['version']}"),
                    os.path.join(server_path, f"{data['type']}.jar"))
        self._servers[id] = MinecraftServer(id, data["name"], datetime.now(), path_data)


    def get_progress(self):
        if self.install_logs != "":
            if self.build_proc is not None and self.build_proc.poll() is None:
                self.install_logs += self.build_proc.communicate()
                return self.install_logs
        else:
            return "No build process running"

    def get_server_status(self, server_id: int) -> dict:
        status = {
            "status": self._get_server(server_id).get_status()
        }
        return status


    def get_server_properties(self):
        pass
