from setuptools import setup, find_packages

setup(
    name="lsp_digital_twin",
    version="3.9.0",
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "pandas",
        "numpy",
        "plotly",
        "scipy",
        "google-generativeai",
        "python-dotenv"
    ],
)
