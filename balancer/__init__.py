VERSION = (0, 4, 0, "f", 1) # following PEP 386
DEV_N = 1 # for PyPi releases, set this to None


def get_version(short=False):
    version = "%s.%s" % (VERSION[0], VERSION[1])
    if short:
        return version
    if VERSION[2]:
        version = "%s.%s" % (version, VERSION[2])
    if VERSION[3] != "f":
        version = "%s%s%s" % (version, VERSION[3], VERSION[4])
        if DEV_N:
            version = "%s.dev%s" % (version, DEV_N)
    return version

__version__ = get_version()

TEST_DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'SUPPORTS_TRANSACTIONS': False,
    },
    'other': {
        'ENGINE': 'django.db.backends.sqlite3',
        'TEST_NAME': 'other_db',
        'TEST_MIRROR': 'default',
        'TEST': {
            'NAME': 'other_db',
            'MIRROR': 'default',
        },
        'SUPPORTS_TRANSACTIONS': False,
    },
    'utility': {
        'ENGINE': 'django.db.backends.sqlite3',
        'TEST_NAME': 'utility_db',
        'TEST': {
            'NAME': 'utility_db',
        },
        'SUPPORTS_TRANSACTIONS': False,
    }
}
TEST_MASTER_DATABASE = 'default'
TEST_DATABASE_POOL = {
    'default': 1,
    'other': 2,
}
