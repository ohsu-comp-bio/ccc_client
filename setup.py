from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, "README.txt"), encoding="utf-8") as readmeFile:
    long_description = readmeFile.read()

setup(
    name="ccc_client",
    description="Command line interface to CCC services",
    long_description=long_description,
    packages=["ccc_client"],
    include_package_data=True,
    zip_safe=False,
    author="Adam Struck",
    author_email="strucka@ohsu.edu",
    url="https://github.com/ohsu-computational-biology/ccc_client",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],
    keywords='tool',
    install_requires=["requests>=2.9.1"],
    entry_points={
        'console_scripts': [
            'ccc_client=ccc_client.cli:cli_main'
        ]
    },
    # Use setuptools_scm to set the version number automatically from Git
    setup_requires=['setuptools_scm'],
    use_scm_version={
        "write_to": "ccc_client/_version.py"
    },
)
