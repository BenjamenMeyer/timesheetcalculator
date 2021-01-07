import sys
from setuptools import setup, find_packages

REQUIRES = [
    'six>=1.11.0'
]

setup(
    name='pytimesheetcalculator',
    version='1.0',
    description='Python-based Time Sheet Calculator',
    license='Apache License 2.0',
    url='',
    author='Benjamen R. Meyer',
    author_email='bm_witness@yahoo.com',
    install_requires=REQUIRES,
    test_suite='pytimesheetcalculator',
    packages=find_packages(exclude=['tests*']),
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'timesheet-calc=pytimesheetcalculator.shell:main'
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3'
    ]
)
