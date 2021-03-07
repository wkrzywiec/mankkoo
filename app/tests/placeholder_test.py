import pytest
import app.scripts.placeholder as placeholder

def placeholder_test():

    value = placeholder.placeholder()
    assert value == 'placeholder'
    