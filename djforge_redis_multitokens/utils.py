
TOKEN_HASH_SEPARATOR = ':hash:'
WRONG_TOKEN = 'wrong_token'
WRONG_HASH = 'wrong_hash'


def make_full_token(token, hash):
    return token + TOKEN_HASH_SEPARATOR + hash


def parse_full_token(full_token):
    token_hash = full_token.split(TOKEN_HASH_SEPARATOR)

    # return bad results so verify function in crypto.py doesn't crash
    # we don't want bad tokens to cause 500 errors on server side
    if len(token_hash) != 2:
        token_hash = ['wrong_token', 'wrong_hash']
    
    return token_hash
