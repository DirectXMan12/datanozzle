from setuptools import setup


setup(
    name='datanozzle',
    version='0.9.0',
    description='A Python client for Datagrepper',
    long_description=open('README.md').read(),
    author='Solly Ross',
    author_email='sross@redhat.com',
    license='GPLv2+',
    url='https://github.com/directxman12/py-datagrepper',
    packages=['datanozzle'],
    install_requires=['requests'],
    keywords='datagrepper',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: Python Software Foundation License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        ('License :: OSI Approved :: GNU General Public '
         'License v2 or later (GPLv2+)')
    ],
)
