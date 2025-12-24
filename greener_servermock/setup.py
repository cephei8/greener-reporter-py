from setuptools import setup

setup(
    name="greener-servermock",
    version="0.0.0",
    description="Python binding for Greener Servermock",
    url="https://greener.cephei8.dev",
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
