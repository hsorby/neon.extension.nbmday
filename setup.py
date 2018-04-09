
"""
A basic Zinc view for the neon application.
"""

from setuptools import setup, find_packages


classifiers = """\
Development Status :: 1 - Planning
Intended Audience :: Developers
Intended Audience :: Education
Intended Audience :: Science/Research
License :: OSI Approved :: Apache Software License
Programming Language :: Python
Operating System :: Microsoft :: Windows
Operating System :: Unix
Operating System :: MacOS :: MacOS X
Topic :: Scientific/Engineering :: Medical Science Apps.
Topic :: Scientific/Engineering :: Visualization
Topic :: Software Development :: Libraries :: Python Modules
"""

doc_lines = __doc__.split("\n")

setup(
    name='neon.extension.nbmday',
    version='0.1.0.dev',
    author='H. Sorby',
    author_email='h.sorby@auckland.ac.nz',
    packages=find_packages('src'),
    package_dir={'':'src'},
    platforms=['any'],
    url='http://pypi.python.org/pypi/neon.extension.nbmday/',
    license='LICENSE',
    description=doc_lines[0],
    classifiers=filter(None, classifiers.split("\n")),
    long_description=open('README.rst').read(),
    install_requires=['pyflakes']
)