import os
import warnings
import uuid
import django
location = lambda x: os.path.join(
    os.path.dirname(os.path.realpath(__file__)), x)


def pytest_addoption(parser):
    parser.addoption(
        '--deprecation', choices=['strict', 'log', 'none'], default='log')


def pytest_configure(config):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')
    # media = 'media_{}'.format(uuid.uuid4())
    # os.environ.setdefault('MEDIA', media)
    # media_root = os.path.join(location('public'), media)
    # os.mkdir(media_root)
    # os.mkdir(os.path.join(media_root, "images"))
    os.environ.setdefault('DJANGO_READ_DOT_ENV_FILE', '1')
    os.environ.setdefault(
        'DATABASE_URL', 'postgres://SUQWOetkbOGJpuXAxliKpZmnyywHdeqm:YZHXsIPZyoBwOUTwAMCLWcJKhYwpwVoeiAhjYMSIqZCBCjAvDBTXUArvSWuhxkgn@postgres:5432/test_{}'.format(uuid.uuid4())
    )

    deprecation = config.getoption('deprecation')
    if deprecation == 'strict':
        warnings.simplefilter('error', DeprecationWarning)
        warnings.simplefilter('error', PendingDeprecationWarning)
        warnings.simplefilter('error', RuntimeWarning)
    if deprecation == 'log':
        warnings.simplefilter('always', DeprecationWarning)
        warnings.simplefilter('always', PendingDeprecationWarning)
        warnings.simplefilter('always', RuntimeWarning)
    elif deprecation == 'none':
        # Deprecation warnings are ignored by default
        pass

    django.setup()
