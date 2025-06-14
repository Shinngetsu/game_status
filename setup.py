# coding : utf-8
from setuptools import setup, find_packages
setup(
    name='game_status',
    version='0.1.0',
    author='Sinngetsu',
    description='A Python package for managing game status effects and buffs',
    long_description=open('README.md', encoding="utf-8").read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Shinngetsu/game_status.git',
    packages=find_packages(),
    license='MIT',
)