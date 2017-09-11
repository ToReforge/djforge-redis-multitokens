from django.test import TestCase

from djforge_redis_multitokens.settings import djforge_redis_multitokens_settings as drf_sett


class TestSettings(TestCase):

    def test_settings_has_all_required_attributes(self):
        self.assertIsNotNone(drf_sett.REDIS_DB_NAME)
        self.assertIsNotNone(drf_sett.RESET_TOKEN_TTL_ON_USER_LOG_IN)
        self.assertIsNotNone(drf_sett.OVERWRITE_NONE_TTL)
        self.assertIsNotNone(drf_sett.TOKEN_TTL_IN_SECONDS)

    def test_user_can_overwrite_default_settings(self):
        # DRF_REDIS_MULTI_TOKENS demo.settings.py overwrites default settings
        self.assertEqual(drf_sett.TOKEN_TTL_IN_SECONDS, 1100000)
