from setuptools import setup, find_packages

setup(
    name="honeyshield",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'flask',
        'flask-socketio',
        'flask-sqlalchemy',
        'python-dotenv',
        'paramiko',
        'requests',
    ],
) 