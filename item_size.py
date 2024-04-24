import decimal

import base64

import math


UTF8_OVERHEAD = 3  # Overhead for UTF-8 encoding

NESTED_OVERHEAD = 1  # Overhead for nested attributes

MAP_LIST_OVERHEAD = 3  # Overhead for maps and lists


def size_in_bytes(item):

    if not item:

        return 0


    size = 0

    for key, value in item.items():

        size += len(key.encode('utf-8')) + UTF8_OVERHEAD

        size += attribute_size_bytes(value)


    return size


def attribute_size_bytes(attribute):

    if not attribute:

        return 0


    if isinstance(attribute, str):

        return len(attribute.encode('utf-8'))


    if isinstance(attribute, (int, float, decimal.Decimal)):

        return number_size_bytes(str(attribute))


    if isinstance(attribute, bytes):

        return len(base64.b64decode(attribute))


    if attribute is True or attribute is False or attribute is None:

        return 1


    if isinstance(attribute, list):

        size = MAP_LIST_OVERHEAD

        for item in attribute:

            size += attribute_size_bytes(item) + NESTED_OVERHEAD

        return size


    if isinstance(attribute, dict):

        size = MAP_LIST_OVERHEAD

        for key, value in attribute.items():

            size += len(key.encode('utf-8')) + UTF8_OVERHEAD

            size += attribute_size_bytes(value) + NESTED_OVERHEAD

        return size


    raise ValueError("Unknown data type: Ensure you are using the correct JSON type (DDB JSON/Native JSON)!")


def number_size_bytes(number_str):

    number = decimal.Decimal(number_str)

    if number == 0:

        return 1


    fixed_number = number.to_eng_string()

    size = measure(fixed_number.lstrip('-')) + 1

    if fixed_number.startswith('-'):

        size += 1


    return min(size, 21)


def measure(number_str):

    if '.' in number_str:

        integer, fraction = number_str.split('.')

        integer = integer or '0'

        fraction = fraction or '0'


        if len(integer) % 2 != 0:

            integer = 'Z' + integer

        if len(fraction) % 2 != 0:

            fraction += 'Z'


        return measure(integer + fraction)


    number_str = number_str.rstrip('Z')

    return math.ceil(len(number_str) / 2)


def calculate_size(item):

    size_in_bytes = size_in_bytes(item)

    rcu = math.ceil(size_in_bytes / 4096)

    wcu = math.ceil(size_in_bytes / 1024)

    return {'rcu': rcu, 'wcu': wcu, 'size': size_in_bytes}


def is_under_limit(item):

    size = calculate_size(item)['size']

    return size < 400_000
