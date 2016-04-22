from setuptools import setup
from setuptools import find_packages

def readme():
    with open('README.md', 'r') as f:
        return f.read()

setup(
    name = 'uchicagoldrtoolsuite',
    version = '0.0.1dev',
    author = "Brian Balsamo, Tyler Danstrom",
    author_email = "balsamo@uchicago.edu, tdanstrom@uchicago.edu",
    packages = find_packages(
        exclude = [
            "build",
            "bin",
            "configs",
            "controlledvocabs",
            "dist",
            "docs",
            "record_configs",
            "tests",
            "uchicagoldr.egg-info"
        ]
    ),
    description = "A suite of tools for working with digital repositories",
    long_description=readme(),
    entry_points = {
        'console_scripts':[
            'ldrstage = uchicagoldrtoolsuite.apps.stager:launch',
            'ldrprune = uchicagoldrtoolsuite.apps.pruner:launch',
            'ldrcreatepremis = uchicagoldrtoolsuite.apps.premiscreator:launch',
            'ldrsetrestriction = uchicagoldrtoolsuite.apps.premisrestrictionsetter:launch',
            'ldrarchive = uchicagoldrtoolsuite.apps.archiver:launch',
            'ldraru = uchicagoldrtoolsuite.apps.aru:launch',
            'ldrpostinstall = uchicagoldrtoolsuite.apps.postinstall:launch'
        ]
    },
    keywords = ["uchicago","repository","file-level","processing"],
    package_data = {
        '': ["*.md"]
    },
    include_package_data=True,
    data_files = [
        ('configs', ['configs/ldr.ini']),
        ('controlledvocabs', [
            'controlledvocabs/filepaths_fits.json',
            'controlledvocabs/filepaths_premis.json',
            'controlledvocabs/filepaths_presform.json',
            'controlledvocabs/restriction_codes.json'
        ]),
        ('record_configs',[
            'record_configs/AccessionRecordFields.csv'
        ])
    ],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "Operating System :: Unix",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    dependency_links = [
        'https://github.com/uchicago-library/uchicagoldr-premiswork' +
        '/tarball/master#egg=pypremis',
        'https://github.com/uchicago-library/uchicagoldr-controlledvocab' +
        '/tarball/master#egg=controlledvocab',
        'https://github.com/uchicago-library/uchicagoldr-hierarchicalrecords' +
        '/tarball/master#egg=hierarchicalrecord',
    ],
    install_requires = ['treelib',
                        'python-magic',
                        'pyxdg',
                        'pypremis',
                        'controlledvocab',
                        'hierarchicalrecord',
                        'requests'])
