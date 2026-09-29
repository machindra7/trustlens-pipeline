from setuptools import setup, find_packages

setup(
    name='trustlens',
    version='1.0.0',
    packages=find_packages(),
    # This tells the installer to specifically grab your top-level scripts
    py_modules=['main', 'ingest_findings'], 
    entry_points={
        'console_scripts': [
            'trustlens=main:main',
        ],
    },
    install_requires=[
        'psycopg2-binary',
        'sqlalchemy'
        'pydantic'
    ],
)