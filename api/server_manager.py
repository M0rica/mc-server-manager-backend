import os
import json
import random
import shutil
import subprocess
from datetime import datetime
from threading import Thread
from typing import Tuple

from api import utils
from api.minecraft_server_versions import AvailableMinecraftServerVersions
from config import get_config
from api.minecraft_server import MinecraftServer, MinecraftServerPathData, MinecraftServerNetworkConfig, \
    MinecraftServerHardwareConfig, MCServerManagerData


class ServerManager:
    def __init__(self, server_versions: AvailableMinecraftServerVersions):
        self.available_versions = server_versions
        self.base_path: str
        self.servers_path: str
        self.build_path: str # directory buildtools is in and where new versions will be build
        self.build_tools_path: str
        self.install_proc: subprocess.Popen = None
        self.install_logs = ""

        self._servers = {}

        self.load_config()
        self.load_servers()

    def load_config(self):
        config = get_config()["servers"]

        self.base_path = config["path"]
        self.servers_path = os.path.join(self.base_path, "servers")

    def load_servers(self):
        file_location = os.path.join(self.servers_path, "servers.json")
        if os.path.isfile(file_location):
            with open(file_location, "r") as f:
                data = json.load(f)
            servers = data["servers"]
            for server_id in servers:
                server_data = servers[server_id]
                print(server_data)
                network_config = MinecraftServerNetworkConfig(**server_data["network_config"])
                hardware_config = MinecraftServerHardwareConfig(**server_data["hardware_config"])
                path_data = MinecraftServerPathData(**server_data["path_data"])
                server_manager_data = MCServerManagerData(**server_data["server_manager_data"])
                server_id = server_data["id"]
                self._servers[server_id] = MinecraftServer(server_id, server_data["name"], path_data, network_config,
                                         hardware_config, server_manager_data, self.available_versions)

    def save_servers(self):
        server_data = self.get_all_server_data()
        save = {
            "servers": server_data
        }
        with open(os.path.join(self.servers_path, "servers.json"), "w") as f:
            json.dump(save, f, default=str, indent=4)

    def server_exists(self, server_id: int) -> bool:
        return server_id in self._servers

    def _get_server(self, server_id: int) -> MinecraftServer:
        server = self._servers.get(server_id)
        if server is not None:
            server.update()
        return server

    def create_server(self, data: dict) -> int:
        id = 0
        while id == 0 or id in self._servers:
            id = random.randint(1000, 9999)
        print(id)
        thrd = Thread(target=self._create_server, args=[id, data])
        thrd.start()
        return id

    def _create_server(self, server_id: int, data: dict):
        server_path = os.path.join(self.servers_path, str(server_id))
        if os.path.exists(server_path):
            shutil.rmtree(server_path)
        os.makedirs(server_path)
        """if data["type"] in ["spigot", "craftbukkit"]:
            build_path = self._bukkit_creator.create_server(data)
            shutil.copy(build_path,
                        os.path.join(server_path, f"{data['type']}.jar"))"""
        path_data = MinecraftServerPathData(base_path=server_path,
                                            absolut_jar_path=os.path.join(server_path, f"{data['type']}.jar"),
                                            jar_path=f"{data['type']}.jar",
                                            server_properties_file=os.path.join(server_path, "server.properties"))
        port = utils.get_free_port()
        network_config = MinecraftServerNetworkConfig(port=port)
        hardware_config = MinecraftServerHardwareConfig(ram=1024)
        server_manager_data = MCServerManagerData(installed=False, version=data["version"], created_at=datetime.now())
        server = MinecraftServer(server_id, data["name"], path_data, network_config, hardware_config, server_manager_data,
                                 self.available_versions)
        self._servers[server_id] = server
        server.install()
        self.save_servers()

    def delete_server(self, server_id: int):
        server = self._get_server(server_id)
        shutil.rmtree(server.path_data.base_path)
        del self._servers[server_id]

    def start_server(self, server_id: int) -> Tuple[bool, str]:
        server = self._get_server(server_id)
        if server is not None:
            success = server.start()
            if success:
                message = "Server started successfully!"
            else:
                status = server.get_status()
                if status == "installing":
                    message = "Couldn't start server: not installed!"
                else:
                    message = "Couldn't start server: already running!"
        else:
            success = False
            message = "Couldn't start server: does not exist!"
        return success, message

    def stop_server(self, server_id: int) -> Tuple[bool, str]:
        server = self._get_server(server_id)
        if server is not None:
            success = server.stop()
            if success:
                message = "Server is stopping"
            else:
                status = server.get_status()
                if status == "stopping":
                    message = "Couldn't stop server: already stopping!"
                else:
                    message = "Couldn't stop server: not running!"
        else:
            success = False
            message = "Couldn't stop server: does not exist!"
        return success, message

    def get_server_ids(self):
        return list(self._servers.keys())

    def get_server_status(self, server_id: int) -> dict:
        status = {
            "status": self._get_server(server_id).get_status()
        }
        return status

    def get_server_data(self, server_id: int) -> dict:
        server = self._get_server(server_id)
        if server is not None:
            return server.__dict__()

    def get_all_server_data(self):
        data = {}
        for id in self._servers.keys():
            data[id] = self.get_server_data(id)
        return data