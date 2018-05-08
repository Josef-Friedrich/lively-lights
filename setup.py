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
    zip_safe=False, )
