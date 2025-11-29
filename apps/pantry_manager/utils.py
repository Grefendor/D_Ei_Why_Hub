"""
Utility Module for Pantry Manager.

Contains helper functions for data extraction and processing.
"""

import re

def extract_weight_or_volume(product):
    """
    Extracts weight or volume information from Open Food Facts product data.

    Args:
        product (dict): The product data dictionary.

    Returns:
        str: The extracted quantity string (e.g., "500g", "1l") or "Unbekannt".
    """
    quantity = product.get('quantity', '')
    if quantity:
        return quantity

    packaging = product.get('packaging', '')
    if packaging:
        match = re.search(r'(\d+(\.\d+)?\s?(ml|g|kg|l))', packaging, re.IGNORECASE)
        if match:
            return match.group(1)

    return "Unbekannt"
