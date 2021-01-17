from setuptools import setup, find_packages

develop = set([
    "ipython==7.17.0",
    "setuptools==50.3.0",
    "twine==3.2.0",
    "wheel==0.35.1",
])

runtime = set([
    "six==1.15.0",
])

docs = set([
    "sphinx==3.2.1",
    "sphinx_rtd_theme==0.5.0",
])

testing = set([
    "coverage==5.2.1",
    "pytest==6.0.1",
    "pytest-cov==2.10.1",
])


if __name__ == "__main__":
    setup(
        name="parsr",
        version="0.4.2",
        description="Parsr is a simple parser combinator library in pure python.",
        long_description=open("README.md").read(),
        long_description_content_type="text/markdown",
        url="https://parsr.readthedocs.io/en/latest/parsr.html",
        packages=find_packages(),
        package_data={"": ["LICENSE"]},
        license="Apache 2.0",
        install_requires=list(runtime),
        extras_require={
            "develop": list(develop | docs | testing),
            "docs": list(runtime | docs),
            "testing": list(runtime | testing),
        },
        classifiers=[
            "Intended Audience :: Developers",
            "Natural Language :: English",
            "License :: OSI Approved :: Apache Software License",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7"
        ],
        include_package_data=True
    )
