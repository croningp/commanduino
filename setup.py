from setuptools import find_packages, setup

VERSION = '0.1.12'

setup(name="commanduino",
      version=VERSION,
      description="A library to interact with an arduino board running Arduino-CommandHandler and derivatives",
      author="Jonathan Grizou",
      author_email='jonathan.grizou@gmail.com',
      platforms=["any"],
      url="https://github.com/croningp/commanduino",
      packages=find_packages(),
      package_data={
            "commanduino": ["*.pyi", "py.typed"]
      },
      include_package_data=True,
      install_requires=['pyserial']
      )
