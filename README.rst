A template to create unifhy-compliant components
================================================

This repository features the package structure and contains the files
one needs to create component(s) that can be used with the Community
Model for the Terrestrial Water Cycle (`unifhy`) Python package.

How to use the template?
------------------------

1. Choose a model name for your component(s) (to replace <model_name> in the
   steps below), following `PEP 8 naming convention
   <https://www.python.org/dev/peps/pep-0008/#package-and-module-names>`_
   i.e. all-lowercase names with underscores if this improves readability only.

2. Create a new local directory using your model name and adding the prefix
   *unifhycontrib-* to it:

.. code-block:: bash

   mkdir unifhycontrib-<model_name>


3. Initialise a local git repository in it:

.. code-block:: bash

   cd unifhycontrib-<model_name>
   git init

4. Download the template source available at
   https://github.com/unifhy-org/unifhycontrib-template (click 'Code' then
   click 'Download ZIP') and place the unzipped source in the newly created
   directory.

5. Rename the existing Python package using your model name:

.. code-block:: bash

   mv unifhycontrib/template unifhycontrib/<model_name>

6. Add and commit those files to the repository:

.. code-block:: bash

   git commit -am "commit template"

7. Create a remote git repository on GitHub and name it
   *unifhycontrib-<model_name>*. Note, using GitHub is not mandatory,
   simply adjust the steps below accordingly if using another host.

8. Set it as a remote repository for your local repository (replace <github_id>
   with your actual GitHub username):

.. code-block:: bash

   git remote add origin https://github.com/<github_id>/unifhycontrib-<model_name>.git

9. Push your commit to the remote repository:

.. code-block:: bash

   git push -u origin main

10. Develop your own component contribution(s) following the `Guide for Contributors
    <https://unifhy-org.github.io/unifhy/for_contributors/preparation.html>`_.

11. List your package dependencies in `<requirements.txt>`_.

12. Overwrite the content in `<README.rst>`_ to describe your component(s).

13. Update the first part of `setup.py <setup.py#L4-L20>`_ with your own details.
