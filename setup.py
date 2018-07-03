from setuptools import setup
import os
import versioneer


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
    url='https://github.com/Josef-Friedrich/lively-lights',
    entry_points = {
        'console_scripts': [
            'lively-lights.py = lively_lights:main',
        ],
    },
    keywords='hue philips',
    install_requires = [
        'ansicolors',
        'astral',
        'flask',
        'phue',
        'Pygments',
        'python-daemon',
        'PyYaml',
        'sphinx-argparse',
    ],
    long_description=read('README.rst'),
    classifiers=[
        'Development Status :: 3 - Alpha',
    ],
)
