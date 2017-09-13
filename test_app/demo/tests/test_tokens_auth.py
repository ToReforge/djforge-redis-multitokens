try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from .utils import (
    create_test_user,
    MockedLibrarySettings,
    MockedSettings,
    SetupTearDownForMultiTokenTests,
)
from djforge_redis_multitokens.tokens_auth import MultiToken, TOKENS_CACHE
from djforge_redis_multitokens.utils import parse_full_token


User = get_user_model()


class TestCreateToken(SetupTearDownForMultiTokenTests, TestCase):

    def test_new_token_has_attributes_required_by_DRF(self):
        self.assertTrue(hasattr(self.token, 'key'))
        self.assertTrue(hasattr(self.token, 'user'))
        self.assertEqual(self.token.user.pk, self.user.pk)

    def test_first_token_for_user_is_flagged_correctly_as_first_device_getting_a_token(self):
        self.assertTrue(self.first_device)

    def test_second_token_for_user_is_flagged_correctly_as_not_the_first_device_getting_a_token(self):
        second_token, first_device = MultiToken.create_token(self.user)
        self.assertFalse(first_device)

    def test_token_is_saved_correctly_in_redis(self):
        self.assertIsNotNone(TOKENS_CACHE.get(self.user.pk))

        hashes = TOKENS_CACHE.get(self.user.pk)
        self.assertEqual(len(hashes), 1)
        self.assertIsNotNone(TOKENS_CACHE.get(hashes[0]))

    def test_only_token_hash_is_saved_in_redis(self):
        hash = TOKENS_CACHE.get(self.user.pk)[0]
        self.assertIsNotNone(TOKENS_CACHE.get(hash))
        self.assertIsNone(TOKENS_CACHE.get(self.token.key))

    def test_second_hash_is_saved_in_redis_alongside_the_first_one(self):
        first_hash = TOKENS_CACHE.get(self.user.pk)[0]
        second_token, first_device = MultiToken.create_token(self.user)
        second_hash = TOKENS_CACHE.get(self.user.pk)[1]

        self.assertEqual(len(TOKENS_CACHE.get(self.user.pk)), 2)
        self.assertIn(first_hash, TOKENS_CACHE.get(self.user.pk))
        self.assertIn(second_hash, TOKENS_CACHE.get(self.user.pk))
        self.assertIsNotNone(TOKENS_CACHE.get(first_hash))
        self.assertIsNotNone(TOKENS_CACHE.get(second_hash))


class TestGetUserFromTokenMethod(SetupTearDownForMultiTokenTests, TestCase):

    def test_correct_user_is_found_for_correct_token(self):
        user = MultiToken.get_user_from_token(self.token.key)
        self.assertEqual(user.pk, self.user.pk)

    def test_exception_is_raised_for_wrong_token(self):
        wrong_token = self.token.key[:-1]
        self.assertRaises(User.DoesNotExist, MultiToken.get_user_from_token, wrong_token)

        wrong_token = self.token.key[1:]
        self.assertRaises(User.DoesNotExist, MultiToken.get_user_from_token, wrong_token)


class TestExpireTokenMethod(SetupTearDownForMultiTokenTests, TestCase):

    def test_token_is_removed_from_redis_when_user_has_only_one_token(self):
        self.assertIsNone(MultiToken.expire_token(self.token))
        self.assertEqual(len(TOKENS_CACHE.get(self.user.pk)), 0)
        _, hash = parse_full_token(self.token.key)
        self.assertIsNone(TOKENS_CACHE.get(hash))

    def test_token_is_removed_from_redis_when_user_has_multiple_tokens(self):
        second_token, first_device = MultiToken.create_token(self.user)
        MultiToken.expire_token(self.token)

        self.assertEqual(len(TOKENS_CACHE.get(self.user.pk)), 1)
        _, hash = parse_full_token(self.token.key)
        self.assertIsNone(TOKENS_CACHE.get(hash))

        self.assertEqual(TOKENS_CACHE.get(self.user.pk)[0], parse_full_token(second_token.key)[1])
        self.assertIsNotNone(TOKENS_CACHE.get(parse_full_token(second_token.key)[1]))

    def test_other_users_tokens_are_not_affected(self):
        second_user = create_test_user('tester2')
        second_token, _ = MultiToken.create_token(second_user)
        MultiToken.expire_token(self.token)

        self.assertIsNotNone(TOKENS_CACHE.get(second_user.pk))
        self.assertIsNotNone(TOKENS_CACHE.get(parse_full_token(second_token.key)[1]))



class TestExpireAllTokenMethod(SetupTearDownForMultiTokenTests, TestCase):

    def test_all_tokens_from_user_are_removed_when_user_has_only_one_token(self):
        self.assertIsNone(MultiToken.expire_token(self.token))
        self.assertEqual(len(TOKENS_CACHE.get(self.user.pk)), 0)
        _, hash = parse_full_token(self.token.key)
        self.assertIsNone(TOKENS_CACHE.get(hash))

    def test_all_tokens_from_user_are_removed_when_user_has_multiple_tokens(self):
        second_token, first_device = MultiToken.create_token(self.user)
        MultiToken.expire_token(self.token)

        self.assertEqual(len(TOKENS_CACHE.get(self.user.pk)), 1)
        _, hash = parse_full_token(self.token.key)
        self.assertIsNone(TOKENS_CACHE.get(hash))

        self.assertEqual(TOKENS_CACHE.get(self.user.pk)[0], parse_full_token(second_token.key)[1])
        self.assertIsNotNone(TOKENS_CACHE.get(parse_full_token(second_token.key)[1]))

    def test_other_users_are_not_affected(self):
        second_user = create_test_user('tester2')
        second_token, _ = MultiToken.create_token(second_user)
        MultiToken.expire_all_tokens(self.user)

        self.assertIsNotNone(TOKENS_CACHE.get(second_user.pk))
        self.assertIsNotNone(TOKENS_CACHE.get(parse_full_token(second_token.key)[1]))


class TestSetValueInCacheMethod(SetupTearDownForMultiTokenTests, TestCase):

    @patch('djforge_redis_multitokens.tokens_auth.settings', new=MockedSettings(timeout=None))
    def test_default_timeout_for_cache_db_is_used_when_timeout_is_not_provided_provided(self):
        MultiToken._set_key_value('key', 'value')
        self.assertIsNone(TOKENS_CACHE.ttl('key'))

    @patch('djforge_redis_multitokens.tokens_auth.settings', new=MockedSettings(timeout=1000))
    def test_token_ttl_is_correct_when_user_provides_cache_db_timeout_parameter(self):
        MultiToken._set_key_value('key', 'value')
        self.assertIsNotNone(TOKENS_CACHE.ttl('key'))
        self.assertAlmostEquals(TOKENS_CACHE.ttl('key'), 1000)


class TestResetTokensTTLMethod(SetupTearDownForMultiTokenTests, TestCase):

    @patch('djforge_redis_multitokens.tokens_auth.settings', new=MockedSettings(timeout=1000))
    def test_users_immortal_tokens_get_limited_ttl_when_OVERWRITE_NONE_TTL_setting_is_True(self):
        hash = TOKENS_CACHE.get(self.user.pk)[0]
        self.assertIsNone(TOKENS_CACHE.ttl(self.user.pk))
        self.assertIsNone(TOKENS_CACHE.ttl(hash))

        MultiToken.reset_tokens_ttl(self.user.pk)
        self.assertIsNotNone(TOKENS_CACHE.ttl(self.user.pk))
        self.assertIsNotNone(TOKENS_CACHE.ttl(hash))

    @patch('djforge_redis_multitokens.tokens_auth.settings', new=MockedSettings(timeout=None))
    @patch('djforge_redis_multitokens.tokens_auth.drt_settings', new=MockedLibrarySettings(overwrite_ttl=False))
    def test_users_immortal_tokens_stay_immortal_when_OVERWRITE_NONE_TTL_setting_is_False(self):
        hash = TOKENS_CACHE.get(self.user.pk)[0]
        MultiToken.reset_tokens_ttl(self.user.pk)

        self.assertIsNone(TOKENS_CACHE.ttl(self.user.pk))
        self.assertIsNone(TOKENS_CACHE.ttl(hash))

    @patch('djforge_redis_multitokens.tokens_auth.settings', new=MockedSettings(timeout=1000))
    def test_other_users_tokens_are_not_affected(self):
        second_user = create_test_user('tester2')
        second_token, _ = MultiToken.create_token(second_user)
        import time
        time.sleep(1)
        MultiToken.reset_tokens_ttl(self.user.pk)

        self.assertEqual(TOKENS_CACHE.ttl(self.user.pk), 1000)
        self.assertNotEqual(TOKENS_CACHE.ttl(second_user.pk), 1000)
        hash = TOKENS_CACHE.get(second_user.pk)[0]
        self.assertNotEqual(hash, 1000)

    @patch('djforge_redis_multitokens.tokens_auth.settings', new=MockedSettings(timeout=1000))
    @patch('djforge_redis_multitokens.tokens_auth.drt_settings', new=MockedLibrarySettings())
    def test_correct_ttl_is_set_for_renewed_tokens(self):
        hash = TOKENS_CACHE.get(self.user.pk)[0]
        MultiToken.reset_tokens_ttl(self.user.pk)

        self.assertAlmostEquals(TOKENS_CACHE.ttl(self.user.pk), 1000)
        self.assertAlmostEquals(TOKENS_CACHE.ttl(hash), 1000)

    @patch('djforge_redis_multitokens.tokens_auth.settings', new=MockedSettings())
    def test_immortal_tokens_stay_immortal_when_user_doesnt_provide_timeout(self):
        hash = TOKENS_CACHE.get(self.user.pk)[0]
        self.assertIsNone(TOKENS_CACHE.ttl(self.user.pk))
        self.assertIsNone(TOKENS_CACHE.ttl(hash))
        MultiToken.reset_tokens_ttl(self.user.pk)

        self.assertIsNone(TOKENS_CACHE.ttl(self.user.pk))
        self.assertIsNone(TOKENS_CACHE.ttl(hash))

    @patch('djforge_redis_multitokens.tokens_auth.settings', new=MockedSettings(timeout=None))
    def test_immortal_tokens_stay_immortal_when_user_provided_timeout_is_None(self):
        hash = TOKENS_CACHE.get(self.user.pk)[0]
        self.assertIsNone(TOKENS_CACHE.ttl(self.user.pk))
        self.assertIsNone(TOKENS_CACHE.ttl(hash))
        MultiToken.reset_tokens_ttl(self.user.pk)

        self.assertIsNone(TOKENS_CACHE.ttl(self.user.pk))
        self.assertIsNone(TOKENS_CACHE.ttl(hash))

    @patch('djforge_redis_multitokens.tokens_auth.settings')
    def test_token_with_ttl_becomes_immortal_when_user_changes_timeout_to_None(self, mocked_settings):
        hash = TOKENS_CACHE.get(self.user.pk)[0]
        TOKENS_CACHE.expire(self.user.pk, 1000)
        TOKENS_CACHE.expire(TOKENS_CACHE.ttl(hash), 1000)

        settings = MockedSettings(timeout=None)
        mocked_settings.CACHES.__getitem__.return_value = settings.CACHES['default']
        MultiToken.reset_tokens_ttl(self.user.pk)

        self.assertIsNone(TOKENS_CACHE.ttl(self.user.pk))
        self.assertIsNone(TOKENS_CACHE.ttl(hash))

    @patch('djforge_redis_multitokens.tokens_auth.settings')
    def test_token_with_ttl_gets_new_ttl_when_user_changes_timeout_to_2000(self, mocked_settings):
        hash = TOKENS_CACHE.get(self.user.pk)[0]
        TOKENS_CACHE.expire(self.user.pk, 1000)
        TOKENS_CACHE.expire(TOKENS_CACHE.ttl(hash), 1000)

        settings = MockedSettings(timeout=2000)
        mocked_settings.CACHES.__getitem__.return_value = settings.CACHES['default']
        MultiToken.reset_tokens_ttl(self.user.pk)

        self.assertEqual(TOKENS_CACHE.ttl(self.user.pk), 2000)
        self.assertEqual(TOKENS_CACHE.ttl(hash), 2000)
