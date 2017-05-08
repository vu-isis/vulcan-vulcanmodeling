# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

from vulcanmodeling import __version__

PROJECT_DESCRIPTION = '''
VulcanModeling implements modeling extensions to the Vulcan framework.
'''

setup(
    name='VulcanModeling',
    version=__version__,
    description='Base distribution of the VulcanModeling framework annex',
    long_description=PROJECT_DESCRIPTION,
    author='Vanderbilt Univerity',
    author_email='larry.howard@vanderbilt.edu',
    url='',
    keywords='webgme vulcanforge turbogears pylons jinja2 mongodb',
    license='MIT',
    platforms=['Linux'],
    classifiers=[
        'Framework :: Pylons',
        'Framework :: TurboGears',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Framework',
        'License :: OSI Approved :: MIT',
    ],
    install_requires=[
        "VulcanForge",
        "PyJWT"
    ],
    include_package_data=True,
    dependency_links=[
        "git+http://git.vulcan.isis.vanderbilt.edu/projects/vulcan/vulcanforge@v2.0.0#egg=VulcanForge",
        "git+https://git.code.sf.net/p/merciless/code@pymongo-30#egg=Ming"
    ],
    setup_requires=["PasteScript >= 1.7", "setuptools_git >= 0.3"],
    paster_plugins=[
        'PasteScript', 'Pylons', 'TurboGears2', 'tg.devtools', 'Ming'],
    packages=find_packages(exclude=['ez_setup']),
    test_suite='nose.collector',
    tests_require=[
        'WebTest >= 1.2', 'BeautifulSoup < 4.0', 'pytidylib', 'poster', 'nose'],
    message_extractors={
        'vulcanforge': [
            ('**.py', 'python', None),
            ('templates/**.mako', 'mako', None),
            ('templates/**.html', 'jinja', None),
            ('static/**', 'ignore', None)]
    },
    entry_points="""
    """
)

