=========================
Djforge Redis Multitokens
=========================

.. image:: https://img.shields.io/pypi/pyversions/djforge-redis-multitokens.svg
  :alt: PyPi Status
  :target: https://pypi.org/project/djforge_redis_multitokens/

.. image:: https://travis-ci.org/ToReforge/djforge-redis-multitokens.svg?branch=master
  :alt: Build Status
  :target: https://travis-ci.org/ToReforge/djforge-redis-multitokens?branch=master

.. image:: https://coveralls.io/repos/github/ToReforge/djforge-redis-multitokens/badge.svg?branch=master
  :alt: Codecov
  :target: https://coveralls.io/github/ToReforge/djforge-redis-multitokens?branch=master

**Compatible with: Python: 2.7, 3.4, 3.5, 3.6  Django: 1.10, 1.11  DRF: 3.6**

What Does djforge-redis-multitokens Do?
=======================================

The djforge-redis-multitokens is a plugin for Django Rest Framework that allows you to create multiple tokens for each
user(one per device or browser) and store them in Redis. Here's why you may want to use this plugin:

- Your users have multiple devices and a log out from one device(or browser) should not log the user out on other devices(or browsers)
- Token retrieval, validation, and updates should be fast. This plugin uses Redis, can't touch this!
- Security is important to you. This plugin encrypts users' tokens so even if an attacker gets access to all your tokens they would not be able to do anything with them.

*Note: device in this document means a physical one or a browser.*

How to Install
==============

First, download the package and install it using pip:

.. code-block:: bash

    pip install git+https://github.com/ToReforge/djforge-redis-multitokens

Or simple:

.. code-block:: bash

    pip install djforge-redis-multitokens

Then, you'll need Django, Django REST Framework, and Redis. Finally, your Django app needs to be able to talk to Redis, so you'll need a library like ``django-redis`` or ``django-redis-cache``. Follow the instructions here(http://django-redis-cache.readthedocs.io/en/latest/intro_quick_start.html) to setup Django with Redis.

How to Use It
=============

Create a Redis DB For Tokens
----------------------------

Once you're done with the installation step, make a Redis db for your tokens in your Django settings file:

.. code-block:: python

   CACHES = {
        # other Redis db definitions above

        # tokens db definition
        'tokens': {
            'BACKEND': 'redis_cache.RedisCache',
            'LOCATION': 'localhost:6379',
            'OPTIONS': {
                'DB': 2,
            },
            'TIMEOUT': None,
        }
    }


**Notes:**

- In the above definition, we're setting "tokens" as the name for the Redis db that will contain tokens. You can change this name, more on that later.
- ``TIMEOUT`` is used to expire tokens. ``TIMEOUT: 10000`` means that new tokens will be valid for 10000 before they expire and are removed from Redis.

Custom Settings
---------------

.. code-block:: python

    DJFORGE_REDIS_MULTITOKENS = {
        'REDIS_DB_NAME': 'custom_redis_db_name_for_tokens',
        'RESET_TOKEN_TTL_ON_USER_LOG_IN': True,
        'OVERWRITE_NONE_TTL': True,
    }

Put the above in your Django settings module to customize the behavior of ``djforge-redis-multitokens``:

- ``REDIS_DB_NAME``: set this to the same name you defined for your Redis db("tokens" in the above defnition).
- ``RESET_TOKEN_TTL_ON_USER_LOG_IN`` extends the life of tokens by ``TIMEOUT`` seconds(set in ``settings.CACHES``).
- ``OVERWRITE_NONE_TTL`` will overwrite the previous ttl of ``None`` (``None`` means Redis will never expire your token) set on a token. Set this to `False` if you don't want your immortal tokens to become mortal.
- In other words, if you set ``OVERWRITE_NONE_TTL`` to ``False``, the ttl of tokens with ttl ``None`` will not change. They will never expire.

Setup Token Authentication
--------------------------

There's complicated logic involved in token authentication, but ``Django REST framework(DRF)`` comes with a "pluggable" authentication module that supports token authentication so that ``djforge-redis-multitokens`` can change where tokens are stored.
We want our tokens to be stored in Redis, so we have to change the default authentication class:

.. code-block:: python

    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': (
            ' djforge_redis_multitokens.tokens_auth.CachedTokenAuthentication',
        ),
        # your other DRF configurations goes below
    }

**Note:**
With this setting, we ask DFR to use ``CachedTokenAuthentication`` to check if users have the right token whenever they log in. ``CachedTokenAuthentication`` is a subclass of DRF's ``TokenAuthentication`` which overrides how tokens are fetched from storage.

Create New Tokens
-----------------

Usually, you want to create a new token whenever a user logs in from a new device:

.. code-block:: python

    from  djforge_redis_multitokens.tokens_auth import MultiToken

    # create new token in your login logic
    def login_handler(request):
        token, _ = MultiToken.create_token(request.user) # request object in DRF has a user attribute
        # _ variable is a boolean that denotes whether this is the first token created for this user

**Notes:**

- Before your login handler function is invoked, DRF checks to see if your user has a valid token. So, the above function is not invoked for users who have a valid token.
- `MultiToken.create_token` takes an instance of ``settings.AUTH_USER_MODEL`` which Django calls the ``User`` model.
- The ``_`` variable, if it is `False`, tells you that the user is logged in on another device(or browser).
- The ``token`` object has two attributes: ``key`` and ``user``. DRF expects custom tokens to have these attributes. ``key`` is the string user receives as their token and ``user`` is an instance of the ``settings.AUTH_USER_MODEL`` model.

Expiring Tokens
---------------

When a user logs out(usually by pressing the "log out" button on your user interface), you usually expire the token associated with that device:

.. code-block:: python

    from  djforge_redis_multitokens.tokens_auth import MultiToken

    def logout_handler(request):
        # DFR request object has an `auth` attribute which is of type MultiToken
        MultiToken.expire_token(request.auth)


Sometimes, you want to expire all tokens of a user. For example, user changes his/her password and you want to force log out the user on all devices:

.. code-block:: python

    from  djforge_redis_multitokens.tokens_auth import MultiToken

    # after user changes password
    def password_changed_handler(user):
        MultiToken.expire_all_tokens(user)


Get User From Token
-------------------

When you have access to user's token, you can get the ``user`` associated with that token:

.. code-block:: python

    MultiToken.get_user_from_token(key)

**Notes:**

- Then `key` here is a ``str`` object, so the ``get_user_from_token`` method expects the key as a string.
- ``MultiToken.get_user_from_token`` returns a ``User`` which is defined by ``settings.AUTH_USER_MODEL``.

Immortal Tokens
---------------

If you want your tokens to never expire, you need to do 2 things:

1) Set ``TIMEOUT`` to ``None`` in ``CACHES``:

.. code-block:: python

    CACHES = {

        # other Redis db definitions above

        # tokens db definition
        'tokens': {
            'BACKEND': 'redis_cache.RedisCache',
            'LOCATION': 'localhost:6379',
            'OPTIONS': {
                'DB': 2,
            },
            'TIMEOUT': None,
        }
    }

2) Set ``OVERWRITE_NONE_TTL`` to ``False`` in ``DJFORGE_REDIS_MULTITOKENS``:

.. code-block:: python

    DJFORGE_REDIS_MULTITOKENS = {
        'REDIS_DB_NAME': 'custom_redis_db_name_for_tokens',
        'RESET_TOKEN_TTL_ON_USER_LOG_IN': True,
        'OVERWRITE_NONE_TTL': False,
    }

How to Develop
==============

- Clone the repo, go to the root directory(where ``setup.py`` is)
- ``pip install --editable .``
- ``cd test_app/``
- ``pip install -r requirements``
- ``cd demo``
- ``python manage.py migrate``
- ``python manage.py test``
