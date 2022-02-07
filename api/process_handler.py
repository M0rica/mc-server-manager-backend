import asyncio
import subprocess
import time
from threading import Thread
from typing import List

import psutil
from fastapi import WebSocket


class ProcessDataStream:
    websockets = []

    def add_websocket(self, websocket: WebSocket):
        self.websockets.append(websocket)

    async def send_data(self, data: dict) -> None:
        for websocket in self.websockets:
            try:
                await websocket.send_json(data)
            except:
                self.websockets.remove(websocket)


class ServerProcess(psutil.Popen):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_stream = ProcessDataStream()
        self.stdout_since_last_send = ""
        self.logs = ""
        self.data = {}

    def add_websocket(self, websocket: WebSocket):
        self.data_stream.add_websocket(websocket)

    def read_output(self):
        output = self.stdout.readline()
        if output:
            print(output)
            self.stdout_since_last_send += output
            self.logs += output

    def update_resource_usage(self):
        memory_system = psutil.virtual_memory()
        memory_server = self.memory_full_info()
        self.data = {
            "cpu": {
                "percent": self.cpu_percent()
            },
            "memory": {
                "total": memory_system.total,
                "used": memory_system.used,
                "server": memory_server.uss
            }
        }

    async def get_data(self):
        self.data["stdout"] = self.stdout_since_last_send
        self.stdout_since_last_send = ""
        return self.data

    def send_data(self):
        self.data["stdout"] = self.stdout_since_last_send
        self.data_stream.send_data(self.data)
        self.stdout_since_last_send = ""


class ProcessHandler(Thread):
    processes = {}

    def __init__(self):
        super().__init__(target=self.run)
        self.daemon = True
        self.stop = False

    def get_process(self, pid: int):
        return self.processes.get(pid)

    def process_exists(self, pid: int):
        process = self.get_process(pid)
        if process is not None and process.poll() is None:
            return True
        else:
            return False

    def start_process(self, command: List[str], cwd: str):
        process = ServerProcess(command, cwd=cwd,
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, universal_newlines=True
                               )
        pid = process.pid
        self.processes[pid] = process
        return pid

    def send_input(self, pid: int, message: str):
        process = self.get_process(pid)
        if process is not None:
            process.stdin.write(message)
            process.stdin.flush()

    def run(self) -> None:
        time.sleep(5)
        start_time = time.time()
        while not self.stop:
            time.sleep(0.2)
            for pid in list(self.processes.keys()):
                if psutil.pid_exists(pid):
                    process = self.processes[pid]
                    if time.time() - start_time > 5:
                        process.update_resource_usage()
                        start_time = time.time()
                        #process.send_data()
                    process.read_output()
                    #asyncio.run_coroutine_threadsafe(process.send_data, asyncio.get_running_loop())
                    #process.send_data()

                else:
                    del self.processes[pid]
