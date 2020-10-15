from setuptools import find_packages, setup

console_scripts = """
    [console_scripts]
    mapswipe_workers=mapswipe_workers.mapswipe_workers:cli
    ms=mapswipe_workers.mapswipe_workers:cli
    """

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="mapswipe-workers",
    version="3.0",
    description="Install script for the MapSwipe-Python-Workers.",
    author="B. Herfort, M. Schaub, M. Reinmuth",
    author_email="",
    url="www.mapswipe.org",
    packages=find_packages(exclude=("docs")),
    install_requires=requirements,
    entry_points=console_scripts,
)
