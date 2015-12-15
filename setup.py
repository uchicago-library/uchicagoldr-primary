from distutils.core import setup

setup(
    name = 'uchicagoldr',
    version = '1.0.0',
    author = "Brian Balsamo,Tyler Dnstrom",
    author_email = ["balsamo@uchicago.edu","tdanstrom@uchicago.edu"],
    packages = ['uchicagoldrstaging'],
    description = "A set of classes for staging new files into the repository",
    keywords = ["uchicago","repository","file-level","processing"],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "Operating System :: Unix",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    install_requires = [])
