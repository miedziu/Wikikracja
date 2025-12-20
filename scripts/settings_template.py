# INSTANCE SPECIFIC PARAMETERS

ALLOWED_HOSTS = ['127.0.0.1:8000', '*']

CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1',
]

DEBUG = True

TIME_ZONE = 'Europe/Warsaw'
LANGUAGE_CODE = 'pl'
gettext_lazy = lambda s: s
LANGUAGES = (
    # Turn on more than one only for multi language sites. Normaly use just one
    ('en', gettext_lazy('English')),
    ('pl', gettext_lazy('Polish')),
)

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [ 'redis://127.0.0.1:6379/1', ],
        },
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# voting
WYMAGANYCH_PODPISOW = 2
CZAS_NA_ZEBRANIE_PODPISOW = 365
DYSKUSJA = 3
CZAS_TRWANIA_REFERENDUM = 3

# chat
ARCHIVE_PUBLIC_CHAT_ROOM = 9
DELETE_PUBLIC_CHAT_ROOM = 360  # Applies to public rooms only. Private rooms are deleted together with the user.

UPLOAD_IMAGE_MAX_SIZE_MB = 5
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB

# citizens
ACCEPTANCE = 3
DELETE_INACTIVE_USER_AFTER = 30

# TODO: Group is public or not
GROUP_IS_PUBLIC = True

