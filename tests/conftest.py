import os
import warnings

import django


def pytest_addoption(parser):
    parser.addoption(
        '--deprecation', choices=['strict', 'log', 'none'], default='log')


def pytest_configure(config):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')
    os.environ.setdefault('DJANGO_READ_DOT_ENV_FILE', '1')
    os.environ.setdefault('DATABASE_URL', 'postgres://SUQWOetkbOGJpuXAxliKpZmnyywHdeqm:YZHXsIPZyoBwOUTwAMCLWcJKhYwpwVoeiAhjYMSIqZCBCjAvDBTXUArvSWuhxkgn@postgres:5432/test')

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
