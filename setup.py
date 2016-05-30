from commanduino._version import __version__

from setuptools import find_packages, setup
setup(name="commanduino",
      version=__version__,
      description="A library to interact with an arduino board running Arduino-CommandHandler and derivatives",
      author="Jonathan Grizou",
      author_email='jonathan.grizou@gmail.com',
      platforms=["any"],
      url="https://github.com/croningp/commanduino",
      packages=find_packages(),
      )
