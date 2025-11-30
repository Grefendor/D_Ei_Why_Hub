import sys
import os
import pytest
from src.core.widget_registry import WidgetRegistry
from src.core.paths import WIDGETS_DIR

def test_widget_reinstantiation(qapp):
    """
    Tests that requesting a widget instance twice returns two different objects.
    """
    registry = WidgetRegistry(WIDGETS_DIR)
    
    # We need to ensure there is at least one widget to test with.
    # The 'clock' widget should exist.
    
    print("Getting first instance of clock...")
    w1 = registry.get_widget_instance("clock")
    
    if w1 is None:
        pytest.skip("Clock widget not found, skipping test.")
    
    print("Getting second instance of clock...")
    w2 = registry.get_widget_instance("clock")
    
    assert w1 is not w2, "Registry returned the same instance. This will cause crashes if the first instance was deleted."
