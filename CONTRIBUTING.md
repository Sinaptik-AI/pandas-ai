# 🐼 Contributing to PandasAI

Hi there! We're thrilled that you'd like to contribute to this project. Your help is essential for keeping it great.

## 🤝 How to submit a contribution

To make a contribution, follow the following steps:

1. Fork and clone this repository
2. Do the changes on your fork
3. Submit a pull request

### 📦 Package manager

We use poetry as our package manager. You can install poetry by following the instructions [here](https://python-poetry.org/docs/#installation).

Please DO NOT use pip or conda to install the dependencies. Instead, use poetry:

```bash
poetry install
```

### 🧹 Linting

We use `pylint` to lint our code. You can run the linter by running the following command:

```bash
pylint pandasai examples
```

Make sure that the linter does not report any errors or warnings before submitting a pull request.

### 🧪 Testing

We use `pytest` to test our code. You can run the tests by running the following command:

```bash
pytest
```

Make sure that all tests pass before submitting a pull request.

## 🚀 Release Process

At the moment, the release process is manual. We try to make frequent releases. Usually, we release a new version when we have a new feature or bugfix. A developer with admin rights to the repository will create a new release on GitHub, and then publish the new version to PyPI.
