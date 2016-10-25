from setuptools import setup
from setuptools import find_packages


def readme():
    with open('README.md', 'r') as f:
        return f.read()

setup(
    name = 'uchicagoldrtoolsuite',
    description = "A suite of tools for working with digital repositories",
    long_description = readme(),
    version = '0.0.1dev',
    author = "Brian Balsamo, Tyler Danstrom",
    author_email = "balsamo@uchicago.edu, tdanstrom@uchicago.edu",
    keywords = [
        "uchicago",
        "repository",
        "file-level",
        "processing"
    ],
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
            "uchicagoldrtoolsuite.egg-info"
        ]
    ),
    entry_points = {
        'console_scripts':[
            'ldrstage = uchicagoldrtoolsuite.bit_level.app.stager:launch',
            'ldrprune = uchicagoldrtoolsuite.bit_level.app.pruner:launch',
            'ldrcreatepremis = uchicagoldrtoolsuite.bit_level.app.premiscreator:launch',
            'ldrsetrestriction = uchicagoldrtoolsuite.bit_level.app.premisrestrictionsetter:launch',
            'ldrarchive = uchicagoldrtoolsuite.bit_level.app.archiver:launch',
            'ldraru = uchicagoldrtoolsuite.core.app.aru:launch',
            'ldrpostinstall = uchicagoldrtoolsuite.core.app.postinstall:launch',
            'ldraddadminnote = uchicagoldrtoolsuite.bit_level.app.adminnoteadder:launch',
            'ldraddlegalnote = uchicagoldrtoolsuite.bit_level.app.legalnoteadder:launch',
            'ldraddaccessionrecord = uchicagoldrtoolsuite.bit_level.app.accessionrecordadder:launch',
            'ldrcreatetechmd = uchicagoldrtoolsuite.bit_level.app.technicalmetadatacreator:launch',
            'ldrcreatepresforms = uchicagoldrtoolsuite.bit_level.app.presformcreator:launch',
            'ldrmakeagent = uchicagoldrtoolsuite.core.app.premisagentmaker:launch',
        ]
    },
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
        ('record_configs', [
            'record_configs/DEFAULT_Complete_Accession_Record_Fields.csv',
            'record_configs/DEFAULT_Staging_Accession_Record_Fields.csv'
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
        'https://github.com/bnbalsamo/nothashes' +
        '/tarball/master#egg=nothashes',
    ],
    install_requires = [
        'treelib',
        'pyxdg',
        'pypremis',
        'controlledvocab',
        'hierarchicalrecord',
        'requests',
        'fasteners',
        'python-magic',
        'nothashes'
    ]
)
