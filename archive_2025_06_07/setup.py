# Save this file in the ROOT directory as: setup.py

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="hedge-intelligence",
    version="1.0.0",
    author="Your Name",
    description="AI-powered financial document analysis platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "streamlit",
        "langchain",
        "openai",
        "faiss-cpu",
        "pypdf",
    ],
)