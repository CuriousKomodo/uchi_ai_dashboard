import json

def save_json(data, filename):
    save_file = open(filename, "w")
    json.dump(data, save_file)


def read_json(filename):
    json_file = open(filename, "r")
    data = json.load(json_file)
    return data
