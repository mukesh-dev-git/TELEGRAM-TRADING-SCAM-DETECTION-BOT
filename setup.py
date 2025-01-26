import os
import sys
import subprocess

from setuptools import setup

# Check if Python is installed and the version is compatible
def check_python_version():
    if sys.version_info < (3, 10) or sys.version_info >= (3, 13):
        print("\nError: This application requires Python >= 3.10 and < 3.13. Please install a compatible version.")
        sys.exit(1)

# Ensure pip is installed
def ensure_pip():
    try:
        import pip
    except ImportError:
        print("\nPip is not installed. Installing pip...")
        subprocess.check_call([sys.executable, '-m', 'ensurepip', '--default-pip'])

# Install dependencies from requirements.txt
def install_dependencies():
    try:
        print("\nInstalling dependencies from requirements.txt...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    except Exception as e:
        print(f"\nError: Failed to install dependencies. {e}")
        sys.exit(1)

# Main setup logic
if __name__ == "__main__":
    # Step 1: Check Python version
    check_python_version()

    # Step 2: Ensure pip is installed
    ensure_pip()

    # Step 3: Install dependencies
    install_dependencies()

    # Step 4: Final message
    print("\nSetup complete! You can now run the application.")

# Define the metadata for setuptools
setup(
    name="telegram-scam-detection-bot",
    version="1.0",
    description="A Telegram bot for scam detection using NLP and AI.",
    author="Your Name",
    author_email="your_email@example.com",
    python_requires=">=3.10, <3.13",
    install_requires=[
        "telethon==1.24.0",
        "requests==2.28.1",
        "easyocr==1.6.2",
        "langid==1.1.6",
        "googletrans==4.0.0-rc1",
        "sentence-transformers==2.2.2",
        "transformers==4.24.0",
        "scikit-learn==1.2.2",
        "pandas==1.5.3",
        "rapidfuzz==2.7.0",
        "huggingface-hub==0.11.1",
        "numpy==1.24.3",
        "scikit-image==0.20.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=[],
    include_package_data=True,
)
