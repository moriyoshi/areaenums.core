from setuptools import setup, find_packages
import os

version = '0.0.1'

long_description = (
    open('README.txt').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

setup(name='areaenums.core',
      version=version,
      description="",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        'Topic :: Software Development :: Localization',
        'Topic :: Scientific/Engineering :: GIS',
        ],
      keywords='',
      author='Moriyoshi Koizumi',
      author_email='mozo@mozo.jp',
      url='http://github.com/moriyoshi/areaenums.core',
      license='mit',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['areaenums'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.i18n',
      ],
      tests_require=[
          'mock',
      ],
      test_suite='areaenums.core',
      entry_points="""
      """,
      )
