#!/usr/bin/env python
import os
from setuptools import setup
from setuptools.config import read_configuration
import sys
thisDir=os.path.dirname(__file__)
cfg = read_configuration(os.path.join(thisDir, 'setup.cfg'))

#print(cfg)
cfg["options"].update(cfg["metadata"])
cfg=cfg["options"]

setup(**cfg)
