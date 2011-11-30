from contextlib import contextmanager


class SettingDoesNotExist:
    pass


@contextmanager
def patch_settings(**kwargs):
    """
    Taken from http://stackoverflow.com/a/3519955 and slightly modified.
    """
    from django.conf import settings
    old_settings = []
    for key, new_value in kwargs.items():
        old_value = getattr(settings, key, SettingDoesNotExist)
        old_settings.append((key, old_value))
        setattr(settings, key, new_value)
    try:
        yield
    finally:
        for key, old_value in old_settings:
            if old_value is SettingDoesNotExist:
                delattr(settings, key)
            else:
                setattr(settings, key, old_value)
