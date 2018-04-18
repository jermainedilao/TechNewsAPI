import random
import string
import base64


def _utf8(s):
    if isinstance(s, unicode):
        return s.encode("utf-8")
    assert isinstance(s, str)
    return s


def generate_random_string(length=12):
    return ''.join(
        random.SystemRandom().choice(
            string.ascii_letters + string.digits
        )
        for _ in range(length)
    )


def encode_string_b64(inputString):
    return base64.b64encode(
        inputString.encode("utf-8")
    )


def decode_string_b64(inputString):
    return base64.b64decode(
        inputString
    ).decode('utf-8')


def normalize_email(email):
    return email.lower().strip()

