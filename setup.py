from setuptools import setup

setup(
    name="Chronicle",
    version="0.1",
    packages=[
        "chronicle",
        "chronicle.event",
        "chronicle.harvest",
        "chronicle.summary",
    ],
    author="Sergey Vartanov",
    author_email="me@enzet.ru",
    description="Time line",
    install_requires=[
        "colour",
        "pydantic~=1.10.2",
        "urllib3~=1.26.6",
        "matplotlib",
        "rich",
    ],

)
