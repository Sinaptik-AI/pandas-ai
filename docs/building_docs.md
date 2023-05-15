Example: Building Docs with MkDocs
===============================================

This example shows a basic MkDocs project with Read the Docs. You're encouraged to view it to get inspiration 
and copy & paste from the files in the source code. If you are using Read the Docs for the first time, have a look at 
the official [Read the Docs Tutorial](https://docs.readthedocs.io/en/stable/tutorial/index.html).

📚 [docs/](https://github.com/readthedocs-examples/example-mkdocs-basic/blob/main/docs/)<br>
A basic MkDocs project lives in `docs/`, it was generated using MkDocs defaults. All the `*.md` make up sections in the documentation.

⚙️ [.readthedocs.yaml](https://github.com/readthedocs-examples/example-mkdocs-basic/blob/main/.readthedocs.yaml)<br>
Read the Docs Build configuration is stored in `.readthedocs.yaml`.

⚙️ [mkdocs.yml](https://github.com/readthedocs-examples/example-mkdocs-basic/blob/main/mkdocs.yml)<br>
A basic [MkDocs configuration](https://www.mkdocs.org/user-guide/configuration/) is stored here, including a few extensions for MkDocs and Markdown. Add your own configurations here, such as extensions and themes. Remember that many extensions and themes require additional Python packages to be installed.

📍 [docs/requirements.txt](https://github.com/readthedocs-examples/example-mkdocs-basic/blob/main/docs/requirements.txt) and [docs/requirements.in](https://github.com/readthedocs-examples/example-mkdocs-basic/blob/main/docs/requirements.in)<br>
Python dependencies are [pinned](https://docs.readthedocs.io/en/latest/guides/reproducible-builds.html) (uses [pip-tools](https://pip-tools.readthedocs.io/en/latest/)) here. Make sure to add your Python dependencies to `requirements.txt` or if you choose [pip-tools](https://pip-tools.readthedocs.io/en/latest/), edit `docs/requirements.in` and remember to run to run `pip-compile docs/requirements.in`.

💡 [docs/api.md](https://github.com/readthedocs-examples/example-mkdocs-basic/blob/main/docs/api.md)<br>
We add our example Python module `lumache` in order to auto-generate an API reference. To do this, we use the `:::` syntax, you can read more in the [mkdocstrings documentation](https://mkdocstrings.github.io/).

💡 [docs/usage.md](https://github.com/readthedocs-examples/example-mkdocs-basic/blob/main/docs/usage.md)<br>
We also include some direct links to a function from the API reference, as well as embedding documentation for the example function `lumache.get_random_recipe`. This functionality is also from the [mkdocstrings](https://mkdocstrings.github.io/python/) extension.

💡 [lumache.py](https://github.com/readthedocs-examples/example-mkdocs-basic/blob/main/lumache.py)<br>
API docs are generated for this example Python module - they use *docstrings* directly in the documentation, notice how this shows up in the rendered documentation. We use the [Sphinx convention](https://pythonhosted.org/an_example_pypi_project/sphinx.html#function-definitions) for docstrings, however you are free to edit `mkdocs.yml` to change this option to `google` or `numpy`.

🔢 Git tags versioning<br>
We use a basic versioning mechanism by adding a git tag for every release of the example project. All releases and their version numbers are visible on
[example-mkdocs-basic.readthedocs.io](https://example-mkdocs-basic.readthedocs.io/en/latest/).

📜 [README.md](https://github.com/readthedocs-examples/example-mkdocs-basic/blob/main/README.md)<br>
Contents of this `README.md` are visible on Github and included on [the documentation index page](https://example-mkdocs-basic.readthedocs.io/en/latest/) (Don\'t Repeat Yourself).

⁉️ Questions / comments<br>
If you have questions related to this example, feel free to can ask them as a Github issue [here](https://github.com/readthedocs-examples/example-mkdocs-basic/issues).


Example Project usage
---------------------

This project has a standard MkDocs layout which is built by Read the Docs almost the same way that you would build it locally (on your own laptop!).

You can build and view this documentation project locally - we recommend that you activate [a local Python virtual environment first](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment):

```console
# Install required Python dependencies (MkDocs etc.)
pip install -r docs/requirements.txt

# Run the mkdocs development server
mkdocs serve
```

Using the example in your own project
-------------------------------------

If you are new to Read the Docs, you may want to refer to the [Read the Docs User documentation](https://docs.readthedocs.io/).

If you are copying this code in order to get started with your documentation, you need to:

1. place your `docs/` folder alongside your Python project. If you are starting a new project, you can adapt the `pyproject.toml` example configuration.
1. use your existing project repository or create a new repository on Github, GitLab, Bitbucket or another host supported by Read the Docs.
1. copy `mkdocs.yml`, `.readthedocs.yaml` and the `docs/` folder into your project.
1. customize all the files, replacing example contents.
1. Rebuild the documenation locally to see that it works.
1. *Finally*, register your project on Read the Docs, see [Importing Your Documentation](https://docs.readthedocs.io/en/stable/intro/import-guide.html).


Read the Docs tutorial
----------------------

To get started with Read the Docs, you may also refer to the [Read the Docs tutorial](https://docs.readthedocs.io/en/stable/tutorial/). It provides a full walk-through of building an example project similar to the one in this repository.
