from setuptools import setup, find_namespace_packages


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# information to be updated by contributors
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# model_name: name of the overarching model for the component(s)
model_name = 'template'

# authors: list of the contributors' names
# (firstname followed by lastname, comma-separated list)
authors = 'Jane Doe, John Doe'

# licence: open source licence under which package is distributed
# (see https://choosealicense.com/)
licence = 'GPL-3'

# source_url: remote location of the git repository hosting the source code
source_url = 'https://github.com/unifhy-org/unifhycontrib-template'
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

with open("README.rst", 'r') as fh:
    long_desc = fh.read()

with open("unifhycontrib/{}/version.py".format(model_name.lower()), 'r') as fv:
    exec(fv.read())


def requirements(filename):
    requires = []
    with open(filename, 'r') as fr:
        for line in fr:
            package = line.strip()
            if package:
                requires.append(package)

    return requires


setup(
    name='unifhycontrib-{}'.format(model_name.lower()),

    version=__version__,

    description='unifhy component(s) for the {} model'.format(model_name),
    long_description=long_desc,
    long_description_content_type="text/x-rst",

    author=authors,

    project_urls={
        'Source Code': source_url
    },

    license=licence,

    classifiers=[
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Topic :: Scientific/Engineering :: Hydrology',
    ],

    packages=find_namespace_packages(include=['unifhycontrib.*'],
                                     exclude=['tests']),

    namespace_packages=['unifhycontrib'],

    install_requires=requirements('requirements.txt'),

    zip_safe=False

)

