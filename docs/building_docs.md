Example: Building Docs with MkDocs
===================================

This example shows a basic MkDocs project with Read the Docs. This project is using `mkdocs` with `readthedocs` 
project template.

Some useful links are given below to lear and contribute in the project.

📚 [docs/](https://github.com/readthedocs-examples/example-mkdocs-basic/blob/main/docs/)<br>
A basic MkDocs project lives in `docs/`, it was generated using MkDocs defaults. All the `*.md` make up sections in the documentation.

⚙️ [.readthedocs.yaml](https://github.com/readthedocs-examples/example-mkdocs-basic/blob/main/.readthedocs.yaml)<br>
Read the Docs Build configuration is stored in `.readthedocs.yaml`.

⚙️ [mkdocs.yml](https://github.com/readthedocs-examples/example-mkdocs-basic/blob/main/mkdocs.yml)<br>
A basic [MkDocs configuration](https://www.mkdocs.org/user-guide/configuration/) is stored here, including a few extensions for MkDocs and Markdown. Add your own configurations here, such as extensions and themes. Remember that many extensions and themes require additional Python packages to be installed.

📍 [docs/requirements.txt](https://github.com/readthedocs-examples/example-mkdocs-basic/blob/main/docs/requirements.txt) and [docs/requirements.in](https://github.com/readthedocs-examples/example-mkdocs-basic/blob/main/docs/requirements.in)<br>
Python dependencies are [pinned](https://docs.readthedocs.io/en/latest/guides/reproducible-builds.html) (uses [pip-tools](https://pip-tools.readthedocs.io/en/latest/)) here. Make sure to add your Python dependencies to `requirements.txt` or if you choose [pip-tools](https://pip-tools.readthedocs.io/en/latest/), edit `docs/requirements.in` and remember to run to run `pip-compile docs/requirements.in`.

Example Project usage
---------------------

`Poetry` is the package manager for `pandasai`. In order to build documentation, we have to add requirements in 
development environment. 

This project has a standard MkDocs layout which is built by Read the Docs almost the same way that you would build it 
locally (on your own laptop!).

You can build and view this documentation project locally - we recommend that you activate a `Poetry` environment
and dependency management tool.
```console
# Install required Python dependencies (MkDocs etc.)
poetry insall --with docs
# Run the mkdocs development server
mkdocs serve
```

Project Docs Structure 
----------------------
If you are new to Read the Docs, you may want to refer to the [Read the Docs User documentation](https://docs.readthedocs.io/).

Below is the rundown of documentation structure for `pandasai`, you need to know:

1. place your `docs/` folder alongside your Python project.
2. copy `mkdocs.yml`, `.readthedocs.yaml` and the `docs/` folder into your project root.
3. `docs/API` contains the API documentation created using `docstring`. For any new module, add the links here
4. Project is using standard Google Docstring Style.
5. Rebuild the documenation locally to see that it works.
6. Documentation are hosted on [Read the Docs tutorial](https://docs.readthedocs.io/en/stable/tutorial/)

> Define the release version in `mkdocs.yml` file.

Read the Docs tutorial
----------------------

To get started with Read the Docs, you may also refer to the 
[Read the Docs tutorial](https://docs.readthedocs.io/en/stable/tutorial/). I

With every release, build the documentation manually. 
