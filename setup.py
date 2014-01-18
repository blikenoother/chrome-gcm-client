try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='chrome-gcm-client',
    version='0.0.1',
    author='Chirag',
    author_email='b.like.no.other@gmail.com',
    url='https://github.com/blikenoother/chrome-gcm-client',
    description='Python client for Google Cloud Messaging (GCM) for Chrome Browser',
    long_description=open('README.md').read(),
    packages=['chromegcmclient'],
    keywords='chrome gcm google cloud messaging',
    install_requires=['requests'],
    classifiers = [ 'Development Status :: 1 - Beta',
                    'Intended Audience :: Developers',
                    'Programming Language :: Python',
                    'Topic :: Software Development :: Libraries :: Python Modules']
)
