from setuptools import setup

setup(
    name="greener-servermock",
    version="1.1.0",
    description="Python binding for Greener Servermock",
    url="https://cephei8.github.io/greener",
    author="cephei8",
    author_email="",
    python_requires=">=3.7, <4",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    packages=["greener_servermock"],
    include_package_data=True,
    install_requires=[
        "pydantic",
    ],
)
