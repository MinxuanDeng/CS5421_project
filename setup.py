from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()

setup(
    name = 'pacc',
    version = '0.0.1',
    author = 'Deng Minxuan, Fu Yihao, Li Siwei, Liu Chenyan, Wu Shifan',
    description = 'Postgresql Assertion Constraint Compiler',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = 'https://github.com/MinxuanDeng/CS5421_project',
    py_modules = ['assertionCompiler'],
    packages = find_packages(),
    install_requires = [requirements],
    python_requires='>=3.8',
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    entry_points ={
        "console_scripts": [
            "pacc = assertionCompiler.cli:main"
        ]
    }
)