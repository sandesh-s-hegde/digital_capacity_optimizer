from setuptools import setup, find_packages

setup(
    name="digital_capacity_optimizer",
    version="1.0.0",
    description="AI-Powered Supply Chain Planning for Cloud Infrastructure",
    author="Sandesh Hegde",
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "pandas",
        "numpy",
        "matplotlib",
        "scipy",
        "statsmodels"
    ],
    python_requires=">=3.8",
)