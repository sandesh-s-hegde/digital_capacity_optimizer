from setuptools import setup, find_packages

setup(
    name="lsp_digital_twin",
    version="4.2.5",
    author="Sandesh_S_Hegde",
    author_email="s.sandesh.hegde@gmail.com",
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
