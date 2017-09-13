from django.conf import settings


DEFAULT_DJFORGE_REDIS_MULTITOKENS = {
    'DJFORGE_REDIS_MULTITOKENS':
        {
            'REDIS_DB_NAME': 'tokens',
            'RESET_TOKEN_TTL_ON_USER_LOG_IN': True,
            'OVERWRITE_NONE_TTL': True,
        }
}


class DRFRedisMultipleTokensrSettings:
    def __init__(self, defaults):
        self.defaults = defaults
        self.overrides = getattr(settings, 'DJFORGE_REDIS_MULTITOKENS', {})

    def __getattr__(self, item):
        try:
            return self.overrides[item]
        except KeyError:
            return self.defaults[item]


djforge_redis_multitokens_settings = DRFRedisMultipleTokensrSettings(
    DEFAULT_DJFORGE_REDIS_MULTITOKENS['DJFORGE_REDIS_MULTITOKENS']
)
