from django.conf import settings
from django.core.cache import caches
from django.contrib.auth import get_user_model
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication

from .crypto import generate_new_hashed_token, verify_token
from .settings import djforge_redis_multitokens_settings as drt_settings
from .utils import parse_full_token


TOKENS_CACHE = caches[drt_settings.REDIS_DB_NAME]


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

        cls._set_key_value(str(user.pk), tokens)
        cls._set_key_value(hash, str(user.pk))

        return MultiToken(full_token, user), created

    @classmethod
    def get_user_from_token(cls, full_token):
        token, hash = parse_full_token(full_token)
        if verify_token(token, hash):
            user = get_user_model().objects.get(pk=TOKENS_CACHE.get(hash))
            return user
        else:
            raise get_user_model().DoesNotExist

    @classmethod
    def expire_token(cls, full_token):
        token, hash = parse_full_token(full_token.key)
        user_pk = TOKENS_CACHE.get(hash)
        tokens = TOKENS_CACHE.get(user_pk)

        if tokens and hash in tokens:
            tokens.remove(hash)
            cls._set_key_value(str(user_pk), tokens)

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
        timeout = cls._get_user_provided_ttl()
        key_ttl = TOKENS_CACHE.ttl(key)

        if key_ttl is None and timeout is not None:
            if drt_settings.OVERWRITE_NONE_TTL:
                TOKENS_CACHE.expire(key, timeout)
        elif key_ttl is None and timeout is None:
            pass
        elif key_ttl is not None and timeout is None:
            TOKENS_CACHE.persist(key)
        else:
            TOKENS_CACHE.expire(key, timeout)

    @classmethod
    def _set_key_value(cls, key, value):
        timeout = cls._get_user_provided_ttl()
        TOKENS_CACHE.set(key, value, timeout=timeout)

    @classmethod
    def _get_user_provided_ttl(cls):
        return settings.CACHES[drt_settings.REDIS_DB_NAME].get('TIMEOUT', None)


class CachedTokenAuthentication(TokenAuthentication):

    def authenticate_credentials(self, key):
        try:
            user = MultiToken.get_user_from_token(key)

            if drt_settings.RESET_TOKEN_TTL_ON_USER_LOG_IN:
                MultiToken.reset_tokens_ttl(user.pk)

        except get_user_model().DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token.')

        if not user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted.')

        return (user, MultiToken(key, user))
