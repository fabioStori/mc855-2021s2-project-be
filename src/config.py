import os
import re
import configparser


class Parser:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("options.conf")

    def get(self, section, option, default_value=None):
        try:
            val = self.config.get(section, option)
            if val == "true":
                return True
            elif val == "false":
                return False

            if re.match('[%].*[%]', val):
                val = os.environ[val[1:-1]]

            return val
        except:
            return default_value
