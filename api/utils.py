import os
import socket


def load_properties(filepath: str, sep='=', comment_char='#'):
    """
    Read the file passed as parameter as a properties file
    """
    props = {}
    with open(filepath, "rt") as f:
        for line in f:
            l = line.strip()
            if l and not l.startswith(comment_char):
                key_value = l.split(sep)
                key = key_value[0].strip()
                value = sep.join(key_value[1:]).strip().strip('"')
                props[key] = value
    return props


def save_properties(filepath: str, data: dict, sep='='):
    """
    Save the data dict to file as properties file
    """
    pass


def create_eula(filepath):
    eula_string = "#By changing the setting below to TRUE you are indicating your agreement to our EULA (https://account.mojang.com/documents/minecraft_eula)." \
                  "\n#Mon Mar 20 21:15:37 PDT 2017" \
                  "\neula=false"
    with open(os.path.join(filepath, "eula.txt"), "w") as f:
        f.write(eula_string)


def get_free_port():
    sock = socket.socket()
    sock.bind(("", 0))
    return sock.getsockname()[1]

