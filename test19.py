from __future__ import print_function
from __future__ import unicode_literals

import yaml
from pprint import pprint


def read_yaml(filename):
    with open(filename) as f:
        return yaml.load(f)


filename = "yaml_ex1.yml"
pprint(read_yaml(filename))

