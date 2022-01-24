import configparser
from pathlib import Path
import os

path = Path(__file__)
ROOT_DIR = path.parent.parent.absolute()
config_path = os.path.join(ROOT_DIR, "config.ini")

config = configparser.ConfigParser()
config.read(config_path)

config_dict = dict(config.items("TRANSLATION"))

JSON_PATH = config_dict.get("jsonpath", "../src/assets/i18n")
