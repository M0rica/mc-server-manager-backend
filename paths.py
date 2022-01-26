import os

data_path = os.path.expanduser("~/.local/share/mc-manager")

if not os.path.exists(data_path):
    os.makedirs(data_path)

if not os.path.exists(p := os.path.join(data_path, "jars")):
    os.mkdir(p)