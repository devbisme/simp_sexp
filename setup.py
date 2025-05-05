from setuptools import setup

# Read the content of README file
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="simp_sexp",
    version="0.1.0",
    description="A simple S-expression parser",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Developer",
    author_email="developer@example.com",
    url="https://github.com/user/simp_sexp",
    py_modules=["simp_sexp"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
)