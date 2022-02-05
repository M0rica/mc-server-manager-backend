import os
import subprocess
from datetime import datetime
from dataclasses import dataclass
from api import utils
from mcstatus import MinecraftServer as MCServer


@dataclass
class MinecraftServerNetworkConfig:
    port: int


@dataclass
class MinecraftServerHardwareConfig:
    ram: int


@dataclass
class MinecraftServerPathData:
    path: str
    jar_path: str
    server_properties_file: str

class MinecraftServer:

    def __init__(self, id: int, name: str, created_at: datetime, path_data: MinecraftServerPathData,
                 network_config: MinecraftServerNetworkConfig, hardware_config: MinecraftServerHardwareConfig):
        self.id = id
        self.name = name
        self.created_at = created_at
        self.network_config: MinecraftServerNetworkConfig = network_config
        self.path_data = path_data

        self.server_properties = {}

        self.starting = False
        self.stopping = False

        self._server_proc: subprocess.Popen = None
        self._logs = ""

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
        server = MCServer("localhost", self.port)
        status = server.status()
        return {
            "ping": status.latency,
            "players": status.players.online
        }

    def __dict__(self):
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at,
            "network_config": dict(self.network_config),
            "hardware_config": dict(self.hardware_config),
            "status": self.get_status(),
            "path": dict(self.path_data),
            "server_properties": self.server_properties,
            "online_stats": self.get_server_stats()
        }
