import pytest

pytestmark = pytest.mark.skip(reason="Manual SendGrid notification test, excluded from automated CI runs")

def test_placeholder():
    assert True
