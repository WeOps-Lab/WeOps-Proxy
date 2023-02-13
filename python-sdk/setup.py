from setuptools import setup, find_packages

setup(
    name="weopsproxy",
    version="1.0.2",
    packages=find_packages(),
    install_requires=[
        "PyYaml==6.0",
        "python-consul==1.1.0"
    ]
)
