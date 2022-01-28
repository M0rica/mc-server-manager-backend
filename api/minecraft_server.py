import os
import subprocess
from dataclasses import dataclass
from datetime import datetime
from api import utils


class MinecraftServer:

    def __init__(self, id: int, name: str, created_at: datetime, path_data: dict):
        self.id = id
        self.name = name
        self.created_at = created_at
        self.path = path_data["path"]
        self.jar_path = os.path.join(self.path, path_data["jar"])

        self.server_properties = {}

        self.ram_amount = 1024
        self.starting = False
        self.stopping = False

        self._server_proc: subprocess.Popen = None
        self._logs = ""

    def load_properties(self):
        self.server_properties = utils.load_properties(os.path.join(self.path, "server.properties"))

    def save_properties(self):
        utils.save_properties(os.path.join(self.path, "server.properties"))

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
