from django.contrib.auth import get_user_model

from djforge_redis_multitokens.tokens_auth import MultiToken, TOKENS_CACHE
from djforge_redis_multitokens.settings import djforge_redis_multitokens_settings as drf_settings


User = get_user_model()


def create_test_user(username='tester'):
    return User.objects.create_user(username=username)


class SetupTearDownForMultiTokenTests:

    def setUp(self):
        TOKENS_CACHE.clear()
        self.user = create_test_user()
        self.token, self.first_device = MultiToken.create_token(self.user)

    def tearDown(self):
        # cleanup Redis after tests
        TOKENS_CACHE.clear()


class MockedSettings:

    def __init__(self, timeout=False):
        if timeout is False:
            self.CACHES = {
                drf_settings.REDIS_DB_NAME: {
                }
            }
        else:
            self.CACHES = {
                drf_settings.REDIS_DB_NAME: {
                    'TIMEOUT': timeout
                }
            }


class MockedLibrarySettings:

    def __init__(self, overwrite_ttl=True, ttl_in_seconds=1100000):
        self.REDIS_DB_NAME = drf_settings.REDIS_DB_NAME
        self.RESET_TOKEN_TTL_ON_USER_LOG_IN = True
        self.OVERWRITE_NONE_TTL = overwrite_ttl
        self.TOKEN_TTL_IN_SECONDS = ttl_in_seconds
