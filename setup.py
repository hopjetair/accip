from setuptools import setup, find_packages

# Read the README file for the long description
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# Read the requirements.txt file for dependencies
with open("requirements.txt", "r", encoding="utf-8") as f:
    install_requires = f.read().splitlines()

setup(
    name="accip",  # Package name (used for pip install)
    version="0.1.0",  # Initial version (increment as you release updates)
    description="A Python-based Airline Customer Conversational Intelligence Platform with FastAPI and PostgreSQL.",
    long_description=long_description,
    long_description_content_type="text/markdown",  # Format of the long description
    author="Dominic",  # Your name
    author_email="hopjetair@gmail.com",  # Your email (optional)
    url="https://github.com/hopjetair/accip",  # Project URL (optional)
    license="MIT",  # License (choose one, e.g., MIT, Apache-2.0)
    
    # Package discovery
    packages=find_packages(where="src"),  # Automatically find packages in src/
    package_dir={"": "src"},  # Map the root package to src/
    include_package_data=True,  # Include non-Python files specified in MANIFEST.in

    # Dependencies
    install_requires=install_requires,  # From requirements.txt

    # Optional: Development dependencies (e.g., for testing)
    extras_require={
        "dev": [
            "unittest",  # Already included in Python, but listed for clarity
        ],
    },

    # Optional: Classifiers for PyPI
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

    # Optional: Python version requirement
    python_requires=">=3.8",

    # Optional: Entry points for CLI scripts
    entry_points={
        "console_scripts": [
            "generate-airline-data=src.data.generator:DataGenerator.main",  # Example CLI command
        ],
    },
)