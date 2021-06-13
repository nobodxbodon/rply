# -*- coding: utf-8 -*-
from setuptools import setup


with open("README.rst", encoding="utf-8", mode="r") as f:
    readme = f.read()

setup(
    name="rply-ulang",
    description="RPly 木兰编程语言定制版",
    long_description=readme,
    # duplicated in docs/conf.py and rply/__init__.py
    project_urls={
        "Source": "https://github.com/nobodxbodon/rply",
    },
    version="0.7.16",
    author="Xuan Wu",
    author_email="mulanrevive@gmail.com",
    packages=["rply"],
    install_requires=["appdirs"],
)
