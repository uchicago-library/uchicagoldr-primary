from setuptools import setup

setup(
    name = 'uchicagoldr',
    version = '1.0.0',
    author = "Brian Balsamo,Tyler Danstrom",
    author_email = ["balsamo@uchicago.edu","tdanstrom@uchicago.edu"],
    packages = ['uchicagoldr'],
    description = "A set of classes required for the uchicago ldr",
    keywords = ["uchicago","repository","file-level","processing"],
    scripts = ['bin/uchicagoldr-postinstall'],
    data_files = [
        ('configs', ['configs/ldr.ini']),
        ('controlledvocabs', [
            'controlledvocabs/filepaths_fits.json',
            'controlledvocabs/filepaths_premis.json',
            'controlledvocabs/filepaths_presform.json',
            'controlledvocabs/restriction_codes.json'
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
                        'hierarchicalrecord'])
