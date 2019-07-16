from setuptools import setup, find_packages

setup(
    # Metadata
    name='GymColab',
    version=0.1,
    author='Tolga Ok',
    author_email='tolgaokk@gmail.com',
    url='',
    description='Grid world environments in open AI gym backended by pycolab',
    long_description="",
    license='MIT',

    # Package info
    packages=["gymcolab", ],
    install_requires=["gym",
                      "pycolab",
                      "matplotlib",
                      "numpy",
                      ],
    zip_safe=False
)
