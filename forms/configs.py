import json

CONFIG = {}

with open("config.json") as fd:
	CONFIG = json.load(fd)

def get_value(key):
	return CONFIG[key]["value"]