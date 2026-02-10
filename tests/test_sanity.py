import pytest

def test_basic_math_sanity():
    """
    A simple placeholder test to ensure the CI pipeline is working correctly.
    """
    assert 1 + 1 == 2

def test_imports():
    """
    Ensure critical libraries are installed and importable.
    """
    import streamlit
    import pandas
    import numpy
    import scipy
    assert True
