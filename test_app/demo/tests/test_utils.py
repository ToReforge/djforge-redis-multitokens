from django.test import TestCase

from djforge_redis_multitokens.utils import (
    make_full_token,
    parse_full_token,
    TOKEN_HASH_SEPARATOR,
    WRONG_HASH,
    WRONG_TOKEN,
)


class TestMakeFullTokenFunction(TestCase):

    def test_full_token_has_correct_format(self):
        token = 'token'
        hash = 'hashed_token'
        full_token = make_full_token(token, hash)

        self.assertIn(token, full_token)
        self.assertIn(hash, full_token)
        self.assertIn(TOKEN_HASH_SEPARATOR, full_token)



class TestParseFullTokenFunction(TestCase):

    def setUp(self):
        self.token = 'token'
        self.hash = 'hashed_token'
        self.full_token = make_full_token(self.token, self.hash)

    def test_correct_full_token_is_parsed_correctly(self):
        self.assertEqual(len(parse_full_token(self.full_token)), 2)
        self.assertIn(self.token, parse_full_token(self.full_token))
        self.assertIn(self.hash, parse_full_token(self.full_token))

    def test_bad_full_token_returns_generic_bad_result(self):
        bad_full_token = ' '.join(self.full_token.split(TOKEN_HASH_SEPARATOR))
        self.assertEqual(len(parse_full_token(bad_full_token)), 2)
        self.assertIn(WRONG_TOKEN, parse_full_token(bad_full_token))
        self.assertIn(WRONG_HASH, parse_full_token(bad_full_token))
