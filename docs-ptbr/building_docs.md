Exemplo: Criando documentações com MkDocs
===================================

Este exemplo mostra como criar um projeto básico do MkDocs com o [ Read the Docs](https://about.readthedocs.com/?ref=readthedocs.com), usando  o `mkdocs` com o template do projeto `readthedocs`.

<!-- This example shows a basic MkDocs project with Read the Docs. This project is using `mkdocs` with `readthedocs` project template.-->

Alguns links úteis são fornecidos abaixo para quem quiser aprender e contribuir com o projeto.

<!-- Some useful links are given below to lear and contribute in the project. -->

📚 [docs/](https://github.com/readthedocs-examples/example-mkdocs-basic/blob/main/docs/)<br>

Um exemplo básico de projeto do MkDocs encontra-se na pasta `docs/` e foi gerado utilizando as configurações padrões do MkDocs. Cada arquivo `*.md` representa uma seção na documentação.

<!--A basic MkDocs project lives in `docs/`, it was generated using MkDocs defaults. All the `*.md` make up sections in the documentation.-->

⚙️ [.readthedocs.yaml](https://github.com/readthedocs-examples/example-mkdocs-basic/blob/main/.readthedocs.yaml)<br>

<!-- Read the Docs Build configuration is stored in `.readthedocs.yaml`. -->

A forma de configurar o Read the Docs pode ser encontrada no arquivo `.readthedocs.yaml`.

⚙️ [mkdocs.yml](https://github.com/readthedocs-examples/example-mkdocs-basic/blob/main/mkdocs.yml)<br>

<!-- A basic [MkDocs configuration](https://www.mkdocs.org/user-guide/configuration/) is stored here, including a few extensions for MkDocs and Markdown. Add your own configurations here, such as extensions and themes. Remember that many extensions and themes require additional Python packages to be installed. -->

Uma configuração básica do MkDocs pode ser encontrada [neste link](https://www.mkdocs.org/user-guide/configuration/), incluindo algumas extensões tanto para MkDocs quanto para Markdown. Sintam-se à vontade para criar suas próprias configurações, como extensões, temas, etc. Só é importante ter cuidado porque muitas extensões e temas requerem a instalação de pacotes Python adicionais.


📍 [docs/requirements.txt](https://github.com/readthedocs-examples/example-mkdocs-basic/blob/main/docs/requirements.txt) e [docs/requirements.in](https://github.com/readthedocs-examples/example-mkdocs-basic/blob/main/docs/requirements.in)<br>

<!-- Python dependencies are [pinned](https://docs.readthedocs.io/en/latest/guides/reproducible-builds.html) (uses [pip-tools](https://pip-tools.readthedocs.io/en/latest/)) here. Make sure to add your Python dependencies to `requirements.txt` or if you choose [pip-tools](https://pip-tools.readthedocs.io/en/latest/), edit `docs/requirements.in` and remember to run to run `pip-compile docs/requirements.in`. -->

As dependências do Python são fixadas (utilizando [pip-tools](https://pip-tools.readthedocs.io/en/latest/)) e podem ser encontradas [neste link](https://docs.readthedocs.io/en/latest/guides/reproducible-builds.html). Lembrem-se de adicionar suas dependências Python no arquivo `docs/requirements.txt` . Se optarem por utilizar o `pip-tools` as dependências devem ser adicionadas no arquivo `docs/requirements.in` e, neste caso, lembrar de compilá-las através do comando `pip-compile docs/requirements.in` .


Exemplo de utilização do projeto
---------------------

<!-- `Poetry` is the package manager for `pandasai`. In order to build documentation, we have to add requirements in 
development environment. 

This project has a standard MkDocs layout which is built by Read the Docs almost the same way that you would build it 
locally (on your own laptop!).

You can build and view this documentation project locally - we recommend that you activate a `Poetry` environment
and dependency management tool.
```console
# Install required Python dependencies (MkDocs etc.)
poetry install --with docs
# Run the mkdocs development server
mkdocs serve
``` -->

O `Poetry` é o gerenciador de pacotes do `pandasai` e para reproduzir e visualizar o projeto localmente, é altamente recomendado ativar um ambiente `Poetry` e adicionar os _requirements_ necessários no seu ambiente de desenvolvimento.

Lembrando que este projeto utiliza um _layout_ padrão do MkDocs e é construído pelo Read the Docs de maneira similar à que vocês fariam localmente em seus próprios laptops.

<!-- ```console
# Install required Python dependencies (MkDocs etc.)
poetry install --with docs
# Run the mkdocs development server
mkdocs serve
``` -->

```bash
# Instale as dependências necessárias do Python (MkDocs etc.)

poetry install --with docs

# Execute o servidor de desenvolvimento mkdocs

mkdocs serve
```

Estrutura da documentação do projeto
----------------------

<!-- If you are new to Read the Docs, you may want to refer to the [Read the Docs User documentation](https://docs.readthedocs.io/). -->

Caso nunca tenham utilizado o Read the Docs, considerem ler a documentação em: [Documentação do usuário do Read the Docs](https://docs.readthedocs.io/).

<!-- Below is the rundown of documentation structure for `pandasai`, you need to know: -->

Abaixo está o passo a passo da estrutura da documentação do `pandasai` que você precisará conhecer para reproduzir:

<!-- 1. place your `docs/` folder alongside your Python project.
2. copy `mkdocs.yml`, `.readthedocs.yaml` and the `docs/` folder into your project root.
3. `docs/API` contains the API documentation created using `docstring`. For any new module, add the links here
4. Project is using standard Google Docstring Style.
5. Rebuild the documenation locally to see that it works.
6. Documentation are hosted on [Read the Docs tutorial](https://docs.readthedocs.io/en/stable/tutorial/) -->

1. Coloque a pasta `docs/` junto com seu projeto Python.
2. Copie os arquivos `mkdocs.yml`, `.readthedocs.yaml` e a pasta `docs/` para a raiz do projeto.
3. `docs/API` contém a documentação da API criada usando `docstring`. Para qualquer novo módulo, adicione os links aqui.
4. O projeto está usando o estilo padrão do Google Docstring.
5. Reconstrua a documentação localmente para verificar se ela funciona.
6. A documentação está hospedada no [Read the Docs tutorial](https://docs.readthedocs.io/en/stable/tutorial/)

> Definam a versão de lançamento no arquivo `mkdocs.yml`.

<!-- 

-- Ficou meio repetitivo, será que é mesmo necessário.

Read the Docs tutorial
----------------------

To get started with Read the Docs, you may also refer to the [Read the Docs tutorial](https://docs.readthedocs.io/en/stable/tutorial/). I With every release, build the documentation manually.  -->
