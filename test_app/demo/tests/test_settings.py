from django.test import TestCase

from djforge_redis_multitokens.settings import djforge_redis_multitokens_settings as drf_sett


class TestSettings(TestCase):

    def test_settings_has_all_required_attributes(self):
        self.assertIsNotNone(drf_sett.REDIS_DB_NAME)
        self.assertIsNotNone(drf_sett.RESET_TOKEN_TTL_ON_USER_LOG_IN)
        self.assertIsNotNone(drf_sett.OVERWRITE_NONE_TTL)
