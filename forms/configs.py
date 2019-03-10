import json

CONFIG = dict()

with open("config.json") as fd:
	CONFIG = json.load(fd)

def get_value(key):
	return CONFIG[key]["value"]

def register_opts(opts):
	CONFIG["tax_year"]["value"] = opts.year
	CONFIG["data_file"]["value"] = opts.data
	CONFIG["out_dir"] = { "value": opts.out }