from django.conf import settings
from django.core.cache import caches
from django.contrib.auth import get_user_model
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication

from .crypto import generate_new_hashed_token, verify_token
from .settings import djforge_redis_multitokens_settings as drt_settings
from .utils import parse_full_token


TOKENS_CACHE = caches[drt_settings.REDIS_DB_NAME]
User = get_user_model()


class MultiToken:

    def __init__(self, key, user):
        self.key = key
        self.user = user

    @classmethod
    def create_token(cls, user):
        created = False
        token, hash, full_token = generate_new_hashed_token()
        tokens = TOKENS_CACHE.get(user.pk)

        if not tokens:
            tokens = [hash]
            created = True
        else:
            tokens.append(hash)

        cls._set_value_in_cache(str(user.pk), tokens)
        cls._set_value_in_cache(hash, str(user.pk))

        return MultiToken(full_token, user), created

    @classmethod
    def get_user_from_token(cls, full_token):
        token, hash = parse_full_token(full_token)
        if verify_token(token, hash):
            user = User.objects.get(pk=TOKENS_CACHE.get(hash))
            return user
        else:
            raise User.DoesNotExist

    @classmethod
    def expire_token(cls, full_token):
        token, hash = parse_full_token(full_token.key)
        user_pk = TOKENS_CACHE.get(hash)
        tokens = TOKENS_CACHE.get(user_pk)

        if tokens and hash in tokens:
            tokens.remove(hash)
            cls._set_value_in_cache(str(user_pk), tokens)

        TOKENS_CACHE.delete(hash)

    @classmethod
    def expire_all_tokens(cls, user):
        hashed_tokens = TOKENS_CACHE.get(user.pk)
        for h in hashed_tokens:
            TOKENS_CACHE.delete(h)

        TOKENS_CACHE.delete(user.pk)

    @classmethod
    def reset_tokens_ttl(cls, user_pk):
        cls._reset_token_ttl(user_pk)

        hashed_tokens = TOKENS_CACHE.get(user_pk)
        for h in hashed_tokens:
            cls._reset_token_ttl(h)


    @classmethod
    def _reset_token_ttl(cls, key):
        if TOKENS_CACHE.ttl(key) is None:
            if drt_settings.OVERWRITE_NONE_TTL:
                TOKENS_CACHE.expire(key, drt_settings.TOKEN_TTL_IN_SECONDS)
        else:
            TOKENS_CACHE.expire(key, drt_settings.TOKEN_TTL_IN_SECONDS)

    @classmethod
    def _set_value_in_cache(cls, key, value):
        if 'TIMEOUT' in settings.CACHES[drt_settings.REDIS_DB_NAME]:
            TOKENS_CACHE.set(key, value)
        else:
            TOKENS_CACHE.set(key, value, timeout=drt_settings.TOKEN_TTL_IN_SECONDS)


class CachedTokenAuthentication(TokenAuthentication):

    def authenticate_credentials(self, key):
        try:
            user = MultiToken.get_user_from_token(key)

            if drt_settings.RESET_TOKEN_TTL_ON_USER_LOG_IN:
                MultiToken.reset_tokens_ttl(user.pk)

        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token.')

        if not user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted.')

        return (user, MultiToken(key, user))
