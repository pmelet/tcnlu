from setuptools import setup

setup(name='tcnlu',
      version='0.1',
      description='Format manipulations for NLU platforms',
      url='http://github.com/pmelet/tcnlu',
      author='pmelet',
      author_email='melet.pierre.etienne@gmail.com',
      license='MIT',
      packages=['tcnlu'],
      entry_points = {
         'console_scripts': ['tcnlu=tcnlu.main:main'],
      },
      install_requires = ["argh", "tabulate"],
      zip_safe=False)