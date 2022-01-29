import os
import shutil
import subprocess
import time

import requests

from config import get_config

class BukkitCreator:

    def __init__(self):

        self.base_path: str
        self.build_path: str # directory buildtools is in and where new versions will be build
        self.build_tools_path: str
        self.build_proc: subprocess.Popen = None
        self.install_logs = ""

        self.available_versions = []

        self.load_config()

    def load_config(self):
        print(get_config())
        config = get_config()["bukkit"]

        self.base_path = config["path"]
        self.servers_path = os.path.join(self.base_path, "servers")
        self.build_path = os.path.join(self.base_path, "build")
        self.build_tools_path = os.path.join(self.build_path, "BuildTools.jar")

    def download_buildtools(self, force_reinstall: bool = False):
        if os.path.exists(self.build_path):
            if force_reinstall:
                shutil.rmtree(self.build_path)
            else:
                return
        os.makedirs(self.build_path)
        resp = requests.get(
            "https://hub.spigotmc.org/jenkins/job/BuildTools/lastSuccessfulBuild/artifact/target/BuildTools.jar")
        with open(self.build_tools_path, "wb") as f:
            f.write(resp.content)

    def _build_server(self, version: str, craftbukkit: bool = False):
        if not os.path.exists(self.build_tools_path):
            self.install_logs += "\nDownloading BuildTools..."
            self.download_buildtools()
        if self.build_proc is None:
            print("running buildtools")
            command = ["java", "-jar", "BuildTools.jar", "--rev", version]
            if craftbukkit:
                command += ["--compile", "craftbukkit"]
            self.build_proc = subprocess.Popen(command, cwd=os.path.abspath(self.build_path),
                                               stdin=subprocess.PIPE,
                                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.install_logs = ""
        while self.build_proc.poll() is None:
            print("still building")
            time.sleep(1)

    def create_server(self, data: dict):
        self._build_server(data["version"], data["type"] == "craftbukkit")
        return os.path.join(self.build_path, f"{data['type']}-{data['version']}.jar")

    def get_progress(self):
        if self.install_logs != "":
            if self.build_proc is not None and self.build_proc.poll() is None:
                self.install_logs += self.build_proc.communicate()
                return self.install_logs
        else:
            return "No build process running"

