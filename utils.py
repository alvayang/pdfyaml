#!/bin/env python
#-*- coding: utf-8 -*-
import yaml
try:
    from yaml import CLoader as Loader
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


class ConfigLoader:
    def __init__(self, config_path):
        self.config_file = config_path
        self.template = {}
        self.run()

    def run(self):
        stream = file(self.config_file, 'r')
        self.template = yaml.load(stream)

    def get_config(self, key):
        if self.template.has_key(key):
            return self.template[key]
        else:
            return {}

    def get_object(self, _typ = 'header'):
        try:
            return self.template['page'][_typ]['objects']
        except:
            return []

    def get_header_height(self):
        try:
            return self.template['page']['header']['height']
        except:
            return 0

    def get_page_info(self, key):
        try:
            return self.template['page'][key]
        except:
            return 0



'''
if __name__ == "__main__":
    s = ConfigLoader("report.yaml")

'''
