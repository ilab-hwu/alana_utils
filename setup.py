from setuptools import setup
from setuptools import find_packages


setup(
    name='utils',
    version='0.0.1',
    description='Common helper functions for Alana bots',
    author='Ondrej Dusek, Ioannis Papaioannou',
    author_email='ipapaioannou83@gmail.com',
    url='https://github.com/WattSocialBot/utils',
    download_url='https://github.com/WattSocialBot/utils.git',
    license='MIT',
    packages=find_packages(),
    package_data={},
    install_requires=["flask_restful"]
    )
