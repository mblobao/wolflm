from setuptools import setup, find_packages
import re

__module__ = 'wolflm'
__author__ = []
__author_email__ = []

with open('README.md', 'r', encoding='utf-8') as file:
    long_description = file.read()

with open('LICENSE', 'r', encoding='utf-8') as file:
    __license__ = file.read().split('\n')[0]

with open('requirements.txt', 'r', encoding='utf-8') as file:
    requirements = []  # file.read().split('\n')

for line in long_description.split('\n'):
    body = '\[!\[Version\]\(https://img.shields.io/badge/version-'
    v_match = 'v([0-9]+.[0-9]+.[0-9]+)'
    v_type = '[_]*([A-z_]*)'
    v_end = '[-]*[A-z]*\)\]\(\)'
    if (match := re.fullmatch(body + v_match + v_type + v_end, line)):
        __version__ = match.group(1)
    if line.startswith('<description>') and line.endswith('</description>'):
        short_description = line.replace('<description>', '').replace('</description>', '')
    elif line.startswith('<status>') and line.endswith('</status>'):
        __status__ = line.replace('<status>', '').replace('</status>', '')
    elif line.startswith('<author>') and line.endswith('</author>'):
        au = line.replace('<author>', '').replace('</author>', '').split(' | ')
        __author__.append(au[0])
        __author_email__.append(au[1])


if __name__ == '__main__':
    setup(
        name=__module__,
        version=__version__,
        author=', '.join(__author__),
        author_email=', '.join(__author_email__),
        description=short_description,
        long_description=long_description,
        long_description_content_type='text/markdown',
        url='https://gitlab.com/mblobao/task_organizer',
        classifiers=[
            'Programming Language :: Python :: 3.13',
            __status__,
            'License :: Private',
        ],
        license=__license__,
        packages=find_packages(
            exclude=['img'], include=[__module__.lower(), f'{__module__.lower()}.*']
        ),
        # install_requires=requirements,
        python_requires='>=3.13',
        keywords=[
            
        ]
    )
