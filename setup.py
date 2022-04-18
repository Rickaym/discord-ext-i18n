from setuptools import setup
from re import search, MULTILINE

pkg_name = "i18n"
prj_path = "discord/ext/{}/".format(pkg_name)
prj_name = "discord-ext-{}".format(pkg_name)
descriptors = ("README.md",)
long_description = ""
version = ""

with open("{}/__init__.py".format(prj_path)) as fp:
    version = search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fp.read(), MULTILINE
    ).group(1) # type: ignore

for desc in descriptors:
    try:
        with open(desc) as f:
            long_description += f.read()
    except FileNotFoundError:
        pass

setup(
    name=prj_name,
    version=version,
    description="A extension supporting fully automated i18j translations for bot interface.",
    author="Rickaym",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Rickaym/{}".format(prj_name),
    project_urls={
        "Issue tracker": "https://github.com/Rickaym/{}/issues".format(prj_name),
    },
    license="MIT",
    python_requires=">=3.7",
    packages=[prj_path.replace("/", ".", -1)],
    install_requires=["py-cord>=2.0.0b"],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.10",
    ],
)
