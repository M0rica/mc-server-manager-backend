import os
import subprocess
from dataclasses import dataclass
from datetime import datetime

import requests
from mcstatus import MinecraftServer as MCServer

from api import utils
from api.minecraft_server_versions import AvailableMinecraftServerVersions
from api.process_handler import ProcessHandler
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
    absolut_jar_path: str
    server_properties_file: str


@dataclass
class MCServerManagerData:
    installed: bool
    version: str
    created_at: datetime


@dataclass
class MinecraftData:
    seed: str
    leveltype: str


class MinecraftServer:

    def __init__(self, id: int, name: str, process_handler: ProcessHandler, path_data: MinecraftServerPathData,
                 network_config: MinecraftServerNetworkConfig, hardware_config: MinecraftServerHardwareConfig,
                 server_manager_data: MCServerManagerData, server_versions: AvailableMinecraftServerVersions):
        self.id = id
        self.name = name
        self.process_handler = process_handler
        self.network_config: MinecraftServerNetworkConfig = network_config
        self.hardware_config = hardware_config
        self.path_data = path_data
        self.server_manager_data = server_manager_data
        self.server_versions = server_versions

        self.server_properties = {}
        self.pid = 0

        self.starting = False
        self.stopping = False

        self._server_proc: subprocess.Popen = None
        self._logs = ""

    def install(self, install_data: MinecraftData):
        if not self.server_manager_data.installed:
            if self.server_manager_data.version in self.server_versions.available_versions:
                os.makedirs(self.path_data.base_path, exist_ok=True)
                headers = {
                    "User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:96.0) Gecko/20100101 Firefox/96.0"
                }
                data = requests.get(self.server_versions.get_download_link(self.server_manager_data.version),
                                    headers=headers).content
                with open(self.path_data.absolut_jar_path, "wb") as f:
                    f.write(data)
                create_eula(self.path_data.base_path)
                self.server_manager_data.installed = True

                self.server_properties = {
                    "server-port": self.network_config.port,
                    "query.port": self.network_config.port,
                    "level-name": "world/world",
                    "level-seed": install_data.seed,
                    "level-type": install_data.leveltype,
                }
                self.save_properties()

    def load_properties(self):
        self.server_properties = utils.load_properties(self.path_data.server_properties_file)

    def save_properties(self):
        utils.save_properties(self.path_data.server_properties_file, self.server_properties)

    def update(self):
        self.pid = 0 if not self.process_handler.process_exists(self.pid) else self.pid
        status = self.get_status()
        if status == "stopped":
            if self.stopping:
                self.stopping = False
                self.save_properties()
            self.starting = False
        if self.starting:
            self.starting = "For help, type \"help\"" not in self.process_handler.get_process(self.pid).logs

    def start(self) -> bool:
        if self.server_manager_data.installed and self.pid == 0:
            print(self.path_data.jar_path)
            self.pid = self.process_handler.start_process(
                ["java", f"-Xmx{self.hardware_config.ram}M", f"-Xms{self.hardware_config.ram}M", "-jar",
                 self.path_data.jar_path, "--nogui"], cwd=self.path_data.base_path)
            print("Starting")
            self.starting = True
            return True
        else:
            return False

    def stop(self) -> bool:
        if self.pid != 0:
            if not self.stopping:
                self.process_handler.send_input(self.pid, "stop\n")
                self.stopping = True
                return True
            else:
                return False
        else:
            return False

    def terminate(self):
        if self._server_proc is not None and self._server_proc.poll() is None:
            self._server_proc.terminate()

    def player_command(self, player: str, command: str) -> bool:
        """
        Perform actions on the server that require a command followed by a player name
        :param player: the player's name
        :param command: the command to execute, such as /ban or /kick
        :return:
        """
        if self.get_status() == "running":
            self.process_handler.send_input(self.pid, f"{command} {player}\n")
            return True
        else:
            return False

    def get_status(self) -> str:
        if self.pid != 0:
            if self.starting:
                return "starting"
            elif self.stopping:
                return "stopping"
            else:
                return "running"
        elif not self.server_manager_data.installed:
            return "installing"
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
            "status": self.get_status(),
            "network_config": self.network_config.__dict__,
            "hardware_config": self.hardware_config.__dict__,
            "path_data": self.path_data.__dict__,
            "server_manager_data": self.server_manager_data.__dict__,
            "server_properties": self.server_properties,
            "online_stats": self.get_server_stats()
        }
