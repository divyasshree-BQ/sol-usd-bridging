import base58
def convert_bytes(value, encoding='base58'):
    if encoding == 'base58':
        return base58.b58encode(value).decode()
    return value.hex()