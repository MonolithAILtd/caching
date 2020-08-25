import setuptools
from setuptools import dist, find_packages
dist.Distribution().fetch_build_eggs(['Cython==0.29'])
from Cython.Build import cythonize
from setuptools.command.build_py import build_py as build_py_orig


class CustomBuildPy(build_py_orig):
    """
    subclass build_py so that we collect no .py files inside the built pip package
    this is done by overriding build_packages method with a noop
    """
    def build_packages(self):
        pass


with open("README.md", "r") as fh:
    long_description = fh.read()

directives = {
    'language_level': 3,
    'always_allow_keywords': True
}

setuptools.setup(
    name="caching",
    version="0.0.1",
    author="Maxwell Flitton",
    author_email="maxwell@monolithai.com",
    description="Python package for caching",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MonolithAILtd/caching",
    install_requires=["boto3"],
    packages=find_packages(exclude=("tests",)),
    classifiers=[
        "Development Status :: 4 - Beta"
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3',
    tests_require=['pytest'],
    ext_modules=cythonize("caching/**/*.py", exclude="tests/**/*.py", compiler_directives=directives, nthreads=4),
    cmdclass={'build_py': CustomBuildPy},
    include_package_data=False,
    options={"bdist_wheel": {"universal": "1"}}
)
