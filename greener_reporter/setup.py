from setuptools import setup

setup(
    name="greener-reporter",
    version="0.12.0",
    description="Python binding for Greener Reporter",
    url="https://greener.cephei8.dev",
    author="cephei8",
    author_email="",
    python_requires=">=3.7, <4",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    packages=["greener_reporter"],
    include_package_data=True,
    install_requires=[
        "pydantic",
    ],
)
