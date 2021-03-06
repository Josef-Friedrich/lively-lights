import os

from setuptools import setup, find_packages
import versioneer


def read(file_name):
    """
    Read the contents of a text file and return its content.

    :param str file_name: The name of the file to read.

    :return: The content of the text file.
    :rtype: str
    """
    return open(
        os.path.join(os.path.dirname(__file__), file_name),
        encoding='utf-8'
    ).read()


setup(
    name='lively_lights',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author='Josef Friedrich',
    author_email='josef@friedrich.rocks',
    description=('Lively light scenes on then Philips Hue lamps using Python.'),
    license='MIT',
    packages=find_packages(),
    url='https://github.com/Josef-Friedrich/lively-lights',
    entry_points={
        'console_scripts': [
            'lively-lights.py = lively_lights:main',
        ],
    },
    keywords='hue philips',
    install_requires=[
        'ansicolors==1.1.8',
        'astral==1.10.1',
        'phue==1.1',
        'ping3==2.6.6',
        'Pygments==2.7.4',
        'pyowm==3.1.1',
        'python-daemon==2.2.4',
        'PyYaml==5.4',
        'sphinx-argparse==0.2.5',
    ],
    tests_requires=[
        'freezegun',
    ],
    long_description=read('README.rst'),
    classifiers=[
        'Development Status :: 3 - Alpha',
    ],
)
