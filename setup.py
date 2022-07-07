from setuptools import setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(name="lcr_plot",
      version="1.0.0",
      packages=["lcr_plot"],
      install_requires=requirements)
