from setuptools import setup

setup(
    name='repochecker',
    description='Command line tool to check all git repositories in a directory',
    author='Oli',
    author_email='oli@olillin.com',
    license='MIT',
    py_modules=['main'],
    install_requires=[
        'colorama',
    ],
    entry_points={
        'console_scripts': [
            'repochecker=main:main',
        ]
    },
)