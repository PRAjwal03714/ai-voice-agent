"""
Basic tests for Vanessa AI
"""

def test_imports():
    """Test that all modules can be imported"""
    try:
        import fastapi
        import langchain
        import openai
        assert True
    except ImportError as e:
        assert False, f"Import failed: {e}"

def test_environment():
    """Test environment setup"""
    import os
    # Just check we can access os module
    assert os.name is not None
