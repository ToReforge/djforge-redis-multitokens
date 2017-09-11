import binascii
import os

from passlib.hash import pbkdf2_sha256

from .utils import make_full_token


def generate_new_hashed_token():
    token =  binascii.hexlify(os.urandom(20)).decode()
    hash = pbkdf2_sha256.hash(token)
    full_token = make_full_token(token, hash)

    return token, hash, full_token


def verify_token(token, hash):
    try:
        return pbkdf2_sha256.verify(token, hash)
    except ValueError:
        return False
