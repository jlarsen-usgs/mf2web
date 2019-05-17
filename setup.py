import sys
from setuptools import setup

# trap someone trying to install flopy with something other
#  than python 2 or 3
if not sys.version_info[0] in (2, 3):
    print('Sorry, mf2web not supported in your Python version')
    print('  Supported versions: 2, 3')
    print('  Your version of Python: {}'.format(sys.version_info[0]))
    sys.exit(1)  # return non-zero value for failure


setup(name="mf2web",
      description='mf2web is a Python package to export ' +
                  'modflow models to netcdf for display on the web.',
      author="Josh Larsen",
      author_email="jlarsen@usgs.gov",
      url='https://github.com/jlarsen-usgs/mf2web',
      license='BSD3',
      platforms='Windows, Mac OS-X, Linux',
      install_requires=['flopy',
                        'numpy>=1.9'],
      packages=['mf2web', 'mf2web.seawat', 'mf2web.mt3d', 'mf2web.mf88', 'mf2web.utils'],
      version=0.1)
