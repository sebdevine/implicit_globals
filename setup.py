from setuptools import setup
from os import path
# noinspection PyProtectedMember
from implicit_globals import __version__, __author__, __doc__, __github__, __email__

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="implicit_globals",
    version=__version__,
    py_modules=['implicit_globals'],
    author=__author__,
    author_email=__email__,
    description=__doc__.splitlines()[0],
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    extras_require={},
    python_requires='>=3.6',
    url=__github__,
    keywords="implicit globals decorator functional",
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Intended Audience :: Developers',
        'Topic :: Utilities'
    ]
)
