# Installed Imports
import configparser
import json


class Config:
    def __init__(self, app):
        self.config_parser = configparser.ConfigParser()
        self.config = {}
        self.read_config()
        self.init_app(app)

    def read_config(self):
        self.config_parser.optionxform = lambda option: option
        self.config_parser.read("serverbase.cfg")

        sections = self.config_parser.sections()
        print("Sections found in the configuration file:", sections)

        if "FLASK" not in sections:
            raise Exception("Section 'FLASK' not found in the configuration file.")

        self.config = dict(self.config_parser.items("FLASK"))

    def init_app(self, app):
        app.config.update(self.parse_config())

    def parse_config(self):
        parsed_config = {}
        for key, value in self.config.items():
            parsed_config[key] = self.parse_value(value)
        return parsed_config

    def parse_value(self, value):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
