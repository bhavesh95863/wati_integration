from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in wati_integration/__init__.py
from wati_integration import __version__ as version

setup(
	name="wati_integration",
	version=version,
	description="Integration with wati to send whats app message",
	author="Bhavesh Maheshwari",
	author_email="iambhavesh95863@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
