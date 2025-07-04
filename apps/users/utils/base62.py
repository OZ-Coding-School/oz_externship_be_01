import random
import string


def generate_base62_code(length: int = 6) -> str:
    chars = string.digits + string.ascii_letters
    return "".join(random.choices(chars, k=length))