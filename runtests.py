import sys
import balancer

try:
    from django.conf import settings

    settings.configure(
        DEBUG=True,
        USE_TZ=True,
        ROOT_URLCONF="balancer.urls",
        INSTALLED_APPS=[
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sites",
            "balancer",
        ],
        SITE_ID=1,
        NOSE_ARGS=['-s'],
        MIDDLEWARE_CLASSES=(),
        DATABASES=balancer.TEST_DATABASES,
        MASTER_DATABASE=balancer.TEST_MASTER_DATABASE,
        DATABASE_POOL=balancer.TEST_DATABASE_POOL,
    )

    try:
        import django
        setup = django.setup
    except AttributeError:
        pass
    else:
        setup()

    from django_nose import NoseTestSuiteRunner
except ImportError:
    import traceback
    traceback.print_exc()
    raise ImportError("To fix this error, run: pip install -r test_requirements.txt")


def run_tests(*test_args):
    if not test_args:
        test_args = ['tests']

    # Run tests
    test_runner = NoseTestSuiteRunner(verbosity=1)

    failures = test_runner.run_tests(test_args)

    if failures:
        sys.exit(failures)


if __name__ == '__main__':
    run_tests(*sys.argv[1:])
