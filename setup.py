from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="planetaryconjunctions",
    description="planetaryconjunctions",
    version="0.1.0",
    packages=["planetaryconjunctions"],
    install_requires=[
        "skyfield>=1.4", "pytz>=2022.1", "pandas>=1.4"
    ],
    keywords='astronomy',
    license='GNU',
    include_package_data=True,
    zip_safe=False,
)
