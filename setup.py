from setuptools import setup, find_packages, Command
import os


class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system('rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info')


setup(
    cmdclass={
        'clean': CleanCommand
    },
    name='Rulz',
    version='1.4.0',
    description='BackService for ARG APP',
    author='Enzo D. Grosso',
    author_email='enzo@luziasol.com',
    url='http://www.python.org/sigs/distutils-sig/',
    install_requires=['flask', 'PyMongo', 'flask_cors', 'httplib2', 'reportlab', 'yapsy', 'redis', 'xlrd', 'xlsxwriter', 'pyyaml', 'python-ldap', 'flask-login', 'rauth', 'flask-mongoalchemy', 'M2Crypto', 'python-dateutil']
)
