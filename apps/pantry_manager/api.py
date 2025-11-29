"""
Product API Module.

This module defines the interface and implementation for fetching product information
from external APIs, specifically Open Food Facts.
"""

import requests
from .utils import extract_weight_or_volume

class ProductAPI:
    """
    Abstract base class for product information APIs.
    """
    def get_product_info(self, barcode):
        """
        Retrieves product information for a given barcode.

        Args:
            barcode (str): The product barcode.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method")

class OpenFoodFactsAPI(ProductAPI):
    """
    Implementation of ProductAPI using the Open Food Facts API.
    """
    def get_product_info(self, barcode):
        """
        Fetches product details from Open Food Facts.

        Args:
            barcode (str): The product barcode.

        Returns:
            tuple: A tuple containing (name, category, weight_volume).
                   Returns (None, None, None) if not found or on error.
        """
        url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 1:  # Produkt gefunden
                    product = data.get('product', {})
                    name = product.get('product_name', 'Unbekannt')
                    category = product.get('categories', 'Unbekannt').split(',')[0] if product.get('categories') else 'Unbekannt'
                    gewicht_volumen = extract_weight_or_volume(product)
                    return name, category, gewicht_volumen
        except requests.RequestException:
            pass
        return None, None, None
