# -*- coding: utf-8 -*-
######################################################################
#                                                                    #
# Part of EKIKA CORPORATION PRIVATE LIMITED (Website: ekika.co).     #
# See LICENSE file for full copyright and licensing details.         #
#                                                                    #
######################################################################

from ast import literal_eval
from secrets import choice
import string
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import json
import re
from os import urandom
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.hazmat.primitives import serialization

from odoo.tools import file_open, date_utils


def extract_params(request):
    """
    Extract http_method, body, uri, headers parameters from odoo-request,
    """
    http_method = request.httprequest.method
    body = request.httprequest.form
    uri = request.httprequest.url
    headers = dict(request.httprequest.headers.to_wsgi_list())

    return http_method, body, uri, headers

def generate_string(length=32, characters=None):
    """Generate a random string of given length using characters.

    Args:
        length (int): Length of the secret key (default: 32).
        characters (str): Sequence of characters to use (if not given use a-z, A-Z, 0-9 and punctuation.)

    Returns:
        str: Generated random string.
    """
    characters = string.ascii_letters + string.digits
    return ''.join(choice(characters) for _ in range(length))


def get_manifest_as_dict(manifest):
    """Provide imported __manifest__ of any module function will return dict."""
    manifest_dict = None
    with file_open(manifest.__file__, mode='r') as f:
        manifest_dict = literal_eval(f.read())
    return manifest_dict


def query_param_modifier(url, query_values):
    """Update given query parameter with new value. If not present add it.
    Process: Parse the URL >> parse_qs >> adjust query >> manually join
        query >> unparse components with new query.

    Args:
        query_values (dict): Dictionary that contains Key as query-parameter and
                             Value as query-parameter value.
    """
    url_components = urlparse(url)
    query_params = parse_qs(url_components.query)
    for key,val in query_values.items():
        query_params[key] = [val]
    new_query_string = '&'.join(
        f"{param}={','.join(values)}"
        for param, values in query_params.items()
    )
    return urlunparse(url_components._replace(query=new_query_string))

def compare_dicts(dict1, dict2):
    """
    Compare two dictionaries for equality.

    Args:
        dict1 (dict): The first dictionary.
        dict2 (dict): The second dictionary.

    Returns:
        bool: True if the dictionaries are equal, False otherwise.
    """
    # Convert dictionaries to JSON strings and compare them
    return json.dumps(dict1, sort_keys=True, ensure_ascii=False, default=date_utils.json_default) == json.dumps(dict2, sort_keys=True, ensure_ascii=False, default=date_utils.json_default)

def capitalize_to_odoo_model(model):
    """
    return standard odoo model name from capitalize model name

    e.g: model = SaleOrder
        return => sale.order
    """
    model_list = re.findall('[A-Z][^A-Z]*', model)
    model_name = ".".join([r.lower() for r in model_list])
    return model_name

def convert_model_capitalize(model):
    """
    return Capitalize model name

    e.g: model = sale.order
        return => SaleOrder
    """
    word = ''
    for i in model.split('.'):
        word += i.capitalize()
    return word

def fix_private_key_pem_format(key: str) -> str:
    # Ensure there are no leading or trailing spaces
    key = key.strip()

    # Use regex to extract the header and footer properly
    match = re.match(r"(-----BEGIN [A-Z ]+-----)(.*?)(-----END [A-Z ]+-----)", key, re.DOTALL)

    if not match:
        raise ValueError("Invalid PEM format: Missing or incorrect BEGIN/END headers.")

    # Extract the header, content, and footer
    header, content, footer = match.groups()

    # Clean up the content by removing spaces/newlines and splitting into 64-char lines
    content = content.replace(" ", "").replace("\n", "")
    formatted_content = "\n".join([content[i:i + 64] for i in range(0, len(content), 64)])

    # Reassemble the key in the correct PEM format
    correct_pem = f"{header}\n{formatted_content}\n{footer}"
    return correct_pem

def fix_public_key_pem_format(key: str) -> str:
    # Ensure there are no leading or trailing spaces
    key = key.strip()

    # Check if the key starts and ends with the correct headers/footers
    if not key.startswith("-----BEGIN PUBLIC KEY-----") or not key.endswith("-----END PUBLIC KEY-----"):
        raise ValueError("Invalid PEM format: Missing BEGIN/END header or footer.")

    # Remove the header and footer temporarily for processing the content
    key = key.replace("-----BEGIN PUBLIC KEY-----", "").replace("-----END PUBLIC KEY-----", "").strip()

    # Remove any spaces or extra newlines within the content
    content = key.replace(" ", "").replace("\n", "")

    # Split the content into 64-character lines (as required for PEM format)
    formatted_content = "\n".join([content[i:i + 64] for i in range(0, len(content), 64)])

    # Reassemble the key with proper PEM headers and footers
    correct_pem = f"-----BEGIN PUBLIC KEY-----\n{formatted_content}\n-----END PUBLIC KEY-----"
    return correct_pem

def generate_keys(algorithm_type):
    if algorithm_type.startswith("ES"):  # Elliptic Curve (ES256, ES384, etc.)
        curve_map = {
            "ES256": ec.SECP256R1(),
            "ES256K": ec.SECP256K1(),
            "ES384": ec.SECP384R1(),
            "ES512": ec.SECP521R1()
        }
        curve = curve_map.get(algorithm_type, ec.SECP256R1())

        private_key = ec.generate_private_key(curve)
        public_key = private_key.public_key()

        # Serialize keys
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )

        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    elif algorithm_type.startswith("RS") or algorithm_type.startswith("PS"):  # RSA-based (RS256, PS256, etc.)
        key_size_map = {
            "RS256": 2048, "RS384": 2048, "RS512": 4096,
            "PS256": 2048, "PS384": 2048, "PS512": 4096
        }
        key_size = key_size_map.get(algorithm_type, 2048)

        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size
        )
        public_key = private_key.public_key()

        # Serialize keys
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )

        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    elif algorithm_type.startswith("HS"):  # Symmetric key (HS256, HS384, HS512)
        secret_key = urandom(64)

        # Return the secret key
        return {"secret_key": secret_key.hex()}

    else:
        raise ValueError(f"Unsupported algorithm type: {algorithm_type}")

    # Return the serialized keys (for asymmetric algorithms)
    return {
        "private_key": private_pem.decode(),
        "public_key": public_pem.decode()
    }

def calculate_discount_percentage_per_quantity(product_quantity, unit_price, fixed_discount_per_line):
    """
    Calculate the discount percentage per quantity for a sale order line.

    :param product_quantity: Number of units in the sale order line (int or float)
    :param unit_price: Price of a single unit (float)
    :param fixed_discount_per_line: Total fixed discount applied to the line (float)
    :return: Discount percentage per quantity (float)
    """
    if product_quantity <= 0 or unit_price <= 0:
        raise ValueError("Product quantity and unit price must be greater than zero.")

    # Calculate the total price (without discount)
    total_price = product_quantity * unit_price

    # Avoid division by zero
    if total_price == 0:
        return 0.0

    # Calculate the discount percentage per quantity
    discount_percentage_per_quantity = (fixed_discount_per_line / total_price) * 100.00
    return discount_percentage_per_quantity

def calculate_fixed_discount(product_quantity, unit_price, discount_percentage):
    if product_quantity <= 0 or unit_price <= 0 or discount_percentage < 0:
        return 0  # Handle invalid inputs gracefully

    total_price_before_discount = product_quantity * unit_price
    fixed_discount_per_line = (discount_percentage / 100.00) * total_price_before_discount
    return round(fixed_discount_per_line, 4)  # Rounded to 4 decimal places
