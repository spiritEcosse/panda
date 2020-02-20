#!/usr/bin/env python
"""
Installation script:
To release a new version to PyPi:
- Ensure the version is correctly set in panda.__init__.py
- Run: make release
"""
import os
import re
import sys

from setuptools import find_packages, setup

PROJECT_DIR = os.path.dirname(__file__)

# import panda  # noqa isort:skip

install_requires = [
    "pytz==2019.2",  # https://github.com/stub42/pytz
    "python-slugify==3.0.3",  # https://github.com/un33k/python-slugify
    "Pillow==6.1.0",  # https://github.com/python-pillow/Pillow
    "rcssmin==1.0.6",  # https://github.com/ndparker/rcssmin
    "argon2-cffi==19.1.0",  # https://github.com/hynek/argon2_cffi
    "whitenoise==4.1.3",  # https://github.com/evansd/whitenoise
    "redis==3.3.6",  # https://github.com/antirez/redis
    "celery==4.3.0",  # pyup: < 5.0  # https://github.com/celery/celery
    "django-celery-beat==1.5.0",  # https://github.com/celery/django-celery-beat
    "flower==0.9.3",  # https://github.com/mher/flower
    "python-telegram-bot==11.1.0",  # https://github.com/python-telegram-bot/python-telegram-bot

    # Django
    # ------------------------------------------------------------------------------
    "Django==2.2.4",  # pyup: < 3.0  # https://www.djangoproject.com/
    "django-environ==0.4.5",  # https://github.com/joke2k/django-environ
    "django-model-utils==3.2.0",  # https://github.com/jazzband/django-model-utils
    "django-allauth==0.39.1",  # https://github.com/pennersr/django-allauth
    "django-crispy-forms==1.7.2",  # https://github.com/django-crispy-forms/django-crispy-forms
    "django-compressor==2.3",  # https://github.com/django-compressor/django-compressor
    "django-redis==4.10.0",  # https://github.com/niwinz/django-redis

    # Django REST Framework
    "djangorestframework==3.10.2",  # https://github.com/encode/django-rest-framework
    "coreapi==2.3.3",  # https://github.com/core-api/python-client

    # Django oscar
    "sorl-thumbnail==12.5.0",  # https://pypi.org/project/sorl-thumbnail/
    "elasticsearch>=2.0.0,<3.0.0",  # https://pypi.org/project/elasticsearch/
    "psycopg2==2.8.3",  # https://github.com/psycopg/psycopg2

    # Helpers
    "pyprof2calltree==1.4.4",
    "ipython==7.7.0",

    # Country data
    "pycountry==19.8.18",
]

docs_requires = [
    'Sphinx==2.2.2',
    'sphinxcontrib-napoleon==0.7',
    'sphinxcontrib-spelling==4.3.0',
    'sphinx_rtd_theme==0.4.3',
    'sphinx-issues==1.2.0',
]

test_requires = [
    'WebTest>=2.0,<2.1',
    'coverage>=4.5,<4.6',
    'django-webtest==1.9.4',
    'py>=1.4.31',
    'psycopg2>=2.7,<2.8',
    'pytest>=5.1,<5.2',
    'pytest-django>=3.5,<3.6',
    'pytest-xdist>=1.29,<1.30',
    'tox>=3.14,<3.15',
]

with open(os.path.join(PROJECT_DIR, 'README.rst')) as fh:
    long_description = re.sub(
        '^.. start-no-pypi.*^.. end-no-pypi', '', fh.read(), flags=re.M | re.S)

setup(
    name='panda',
    version="0.1.0",
    url='https://github.com/spiritEcosse/panda',
    author="igor",
    author_email="shenvchenkcoigor@gmail.com",
    description="Sandbox site from oscar",
    long_description=long_description,
    keywords="E-commerce, Django, domain-driven",
    license='BSD',
    platforms=['linux'],
    package_dir={'': 'panda'},
    packages=find_packages('panda'),
    include_package_data=True,
    install_requires=install_requires,
    extras_require={
        'docs': docs_requires,
        'test': test_requires,
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: oscar',
        'Framework :: oscar :: 2.0.1',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Application Frameworks'
    ]
)

# Show contributing instructions if being installed in 'develop' mode
if len(sys.argv) > 1 and sys.argv[1] == 'develop':
    docs_url = ''
    mailing_list = ''
    mailing_list_url = ''
    twitter_url = ''
    msg = (
        "You're installing Oscar in 'develop' mode so I presume you're thinking\n"
        "of contributing:\n\n"
        "(a) That's brilliant - thank you for your time\n"
        "(b) If you have any questions, please use the mailing list:\n    %s\n"
        "    %s\n"
        "(c) There are more detailed contributing guidelines that you should "
        "have a look at:\n    %s\n"
        "(d) Consider following @django_oscar on Twitter to stay up-to-date\n"
        "    %s\n\nHappy hacking!") % (mailing_list, mailing_list_url,
                                       docs_url, twitter_url)
    line = '=' * 82
    print(("\n%s\n%s\n%s" % (line, msg, line)))
