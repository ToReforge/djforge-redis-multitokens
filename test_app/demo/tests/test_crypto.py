from django.test import TestCase

from djforge_redis_multitokens.crypto import generate_new_hashed_token, verify_token
from djforge_redis_multitokens.utils import TOKEN_HASH_SEPARATOR


class TestGenerateNewTokenClass(TestCase):

    def test_function_returns_three_parts(self):
        res = generate_new_hashed_token()
        self.assertEqual(len(res), 3)

    def test_full_token_has_correct_format(self):
        token, hash, full_token = generate_new_hashed_token()
        self.assertIn(TOKEN_HASH_SEPARATOR, full_token)
        self.assertEqual(full_token.split(TOKEN_HASH_SEPARATOR), [token, hash])


class TestVerifyTokenFunction(TestCase):

    def test_token_verification_succeeds_with_correct_token_and_hash(self):
        token, hash, full_token = generate_new_hashed_token()
        self.assertTrue(verify_token(token, hash))

    def test_token_verification_fails_with_incorrect_token(self):
        token, hash, full_token = generate_new_hashed_token()
        token = token[1:]
        self.assertFalse(verify_token(token, hash))

    def test_token_verification_fails_with_incorrect_hash(self):
        token, hash, full_token = generate_new_hashed_token()
        hash = hash[:-1]
        self.assertFalse(verify_token(token, hash))
