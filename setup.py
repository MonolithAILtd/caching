import setuptools
from setuptools import find_packages

with open("./README.md", "r") as fh:
    long_description = fh.read()

with open('./requirements.txt') as f:
    install_requires = f.read().splitlines()

install_requires = [req for req in install_requires if req != '' and not req.startswith('#')]

setuptools.setup(
    name="caching",
    version="0.0.1",
    author="Maxwell Flitton",
    author_email="maxwell@monolithai.com",
    description="Python package for caching",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MonolithAILtd/caching",
    packages=find_packages(include="caching.*", exclude="tests"),
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 4 - Beta"
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
