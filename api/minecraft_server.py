import subprocess
from datetime import datetime
from dataclasses import dataclass

import requests

from api import utils
from mcstatus import MinecraftServer as MCServer

from api.minecraft_server_versions import AvailableMinecraftServerVersions
from api.utils import create_eula


@dataclass
class MinecraftServerNetworkConfig:
    port: int


@dataclass
class MinecraftServerHardwareConfig:
    ram: int


@dataclass
class MinecraftServerPathData:
    base_path: str
    jar_path: str
    server_properties_file: str

@dataclass
class MCServerManagerData:
    installed: bool
    version: str
    created_at: datetime

class MinecraftServer:

    def __init__(self, id: int, name: str, path_data: MinecraftServerPathData,
                 network_config: MinecraftServerNetworkConfig, hardware_config: MinecraftServerHardwareConfig,
                 server_manager_data: MCServerManagerData, server_versions: AvailableMinecraftServerVersions):
        self.id = id
        self.name = name
        self.network_config: MinecraftServerNetworkConfig = network_config
        self.hardware_config = hardware_config
        self.path_data = path_data
        self.server_manager_data = server_manager_data
        self.server_versions = server_versions

        self.server_properties = {}

        self.starting = False
        self.stopping = False

        self._server_proc: subprocess.Popen = None
        self._logs = ""

    def install(self):
        if not self.server_manager_data.installed:
            if self.server_manager_data.version in self.server_versions.available_versions:
                headers = {
                    "User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:96.0) Gecko/20100101 Firefox/96.0"
                }
                data = requests.get(self.server_versions.get_download_link(self.server_manager_data.version),
                                    headers=headers).content
                with open(self.path_data.jar_path, "wb") as f:
                    f.write(data)
                create_eula(self.path_data.base_path)
                self.server_manager_data.installed = True

    def load_properties(self):
        self.server_properties = utils.load_properties(self.path_data.server_properties_file)

    def save_properties(self):
        utils.save_properties(self.path_data.server_properties_file, self.server_properties)

    def update(self):
        if self.get_status() == "stopped":
            if self.stopping:
                self.stopping = False
                self.save_properties()
            self.starting = False
            self._server_proc = None
        elif self._server_proc.poll() is None:
            self._logs += self._server_proc.communicate()
        if self.starting:
            self.starting = "For help, type \"help\"" not in self._logs

    def start(self):
        if self._server_proc is None or self._server_proc.poll() is not None:
            self._server_proc = subprocess.Popen(
                ["java", f"-Xmx{self.ram_amount}M", f"-Xms{self.ram_amount}M", "-jar", self.jar_path, "-o", "true",
                 "--nogui"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.starting = True

    def terminate(self):
        if self._server_proc is not None and self._server_proc.poll() is None:
            self._server_proc.terminate()

    def get_status(self) -> str:
        if self._server_proc is not None and self._server_proc.poll() is None:
            if self.starting:
                return "starting"
            elif self.stopping:
                return "stopping"
            else:
                return "running"
        else:
            return "stopped"

    def get_server_stats(self):
        if self.get_status() == "running":
            server = MCServer("localhost", self.network_config.port)
            status = server.status()
            return {
                "ping": status.latency,
                "players": status.players.online
            }
        else:
            return {}

    def __dict__(self):
        return {
            "id": self.id,
            "name": self.name,
            "network_config": self.network_config.__dict__,
            "hardware_config": self.hardware_config.__dict__,
            "status": self.get_status(),
            "path": self.path_data.__dict__,
            "server_manager_data": self.server_manager_data.__dict__,
            "server_properties": self.server_properties,
            "online_stats": self.get_server_stats()
        }
