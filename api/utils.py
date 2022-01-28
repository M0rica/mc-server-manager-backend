
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

