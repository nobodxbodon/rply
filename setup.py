from setuptools import setup


with open("README.rst") as f:
    readme = f.read()

setup(
    name="rply-ulang",
    description="A pure Python Lex/Yacc that works with RPython，木兰编程语言定制版",
    long_description=readme,
    # duplicated in docs/conf.py and rply/__init__.py
    version="0.7.9",
    author="Xuan Wu",
    author_email="mulanrevive@gmail.com",
    packages=["rply"],
    install_requires=["appdirs"],
)
