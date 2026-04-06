"""Package configuration for pydreo-client."""

from pathlib import Path

from setuptools import find_packages, setup


ROOT = Path(__file__).parent.resolve()
ABOUT = {}
exec((ROOT / "pydreo" / "version.py").read_text(encoding="utf-8"), ABOUT)

setup(
    name="pydreo-client",
    version=ABOUT["__version__"],
    description="Provider-based Dreo SDK with cloud support and local extension points.",
    long_description=(ROOT / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    author="Brooke Wang",
    author_email="developer@dreo.com",
    url="https://github.com/dreo-team/pydreo-client",
    download_url="https://github.com/dreo-team/pydreo-client/archive/refs/tags/v{version}.tar.gz".format(
        version=ABOUT["__version__"]
    ),
    packages=find_packages(include=("pydreo", "pydreo.*")),
    include_package_data=True,
    license="MIT",
    license_files=("LICENSE",),
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.31.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
