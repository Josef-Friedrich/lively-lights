import versioneer
import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='lively_lights',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author='Josef Friedrich',
    author_email='josef@friedrich.rocks',
    description=('Lively light scenes on then Philips Hue lamps using Python.'),
    license='MIT',
    packages=['lively_lights'],
    url='https://github.com/Josef-Friedrich/lively_lights',
    entry_points = {
        'console_scripts': [
            'lively-lights.py = lively_lights:main',
        ],
    },
    install_requires = [
        'astral',
        'flask',
        'phue',
        'python-daemon',
    ],
    long_description=read('README.rst'),
    classifiers=[
        'Development Status :: 3 - Alpha',
    ],
)
