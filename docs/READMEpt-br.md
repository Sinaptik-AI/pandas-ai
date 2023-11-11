# PandasAI 🐼

[![Release](https://img.shields.io/pypi/v/pandasai?label=Release&style=flat-square)](https://pypi.org/project/pandasai/)
[![CI](https://github.com/gventuri/pandas-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/gventuri/pandas-ai/actions/workflows/ci.yml/badge.svg)
[![CD](https://github.com/gventuri/pandas-ai/actions/workflows/cd.yml/badge.svg)](https://github.com/gventuri/pandas-ai/actions/workflows/cd.yml/badge.svg)
[![Coverage](https://codecov.io/gh/gventuri/pandas-ai/branch/main/graph/badge.svg)](https://codecov.io/gh/gventuri/pandas-ai)
[![Documentation Status](https://readthedocs.org/projects/pandas-ai/badge/?version=latest)](https://pandas-ai.readthedocs.io/en/latest/?badge=latest)
[![Discord](https://dcbadge.vercel.app/api/server/kF7FqH2FwS?style=flat&compact=true)](https://discord.gg/kF7FqH2FwS)
[![Downloads](https://static.pepy.tech/badge/pandasai)](https://pepy.tech/project/pandasai) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Open in Colab](https://camo.githubusercontent.com/84f0493939e0c4de4e6dbe113251b4bfb5353e57134ffd9fcab6b8714514d4d1/68747470733a2f2f636f6c61622e72657365617263682e676f6f676c652e636f6d2f6173736574732f636f6c61622d62616467652e737667)](https://colab.research.google.com/drive/1ZnO-njhL7TBOYPZaqvMvGtsjckZKrv2E?usp=sharing)

PandasAI é uma biblioteca Python que adiciona capacidades de Inteligência Artificial Generativa ao pandas, a popular ferramenta de análise e manipulação de dados. Ela é projetada para ser usada em conjunto com o pandas e não substituí-lo.

<!-- Add images/pandas-ai.png -->

![PandasAI](images/pandas-ai.png?raw=true)

## 🔧 Instalação rápida

```bash
pip install pandasai
```

## 🔍 Demonstração

Experimente o PandasAI em seu navegador:

[![Open in Colab](https://camo.githubusercontent.com/84f0493939e0c4de4e6dbe113251b4bfb5353e57134ffd9fcab6b8714514d4d1/68747470733a2f2f636f6c61622e72657365617263682e676f6f676c652e636f6d2f6173736574732f636f6c61622d62616467652e737667)](https://colab.research.google.com/drive/1ZnO-njhL7TBOYPZaqvMvGtsjckZKrv2E?usp=sharing)

## 📖 Documentação

A documentação do PandasAI pode ser encontrada [aqui](https://pandas-ai.readthedocs.io/en/latest/).

## 💻 Uso

> Aviso: Os dados do PIB foram coletados a partir [desta fonte](https://ourworldindata.org/grapher/gross-domestic-product?tab=table), publicados pelo World Development Indicators - Banco Mundial (26/05/2022) e coletados nos dados de contas nacionais - Banco Mundial / OCDE. Isso se refere ao ano de 2020. Os índices de felicidade foram extraídos do [Relatório Mundial da Felicidade](https://ftnnews.com/images/stories/documents/2020/WHR20.pdf). Outro link útil [aqui](https://data.world/makeovermonday/2020w19-world-happiness-report-2020).

O PandasAI é projetado para ser usado em conjunto com o pandas. Ele torna o pandas conversacional, permitindo que você faça perguntas aos seus dados em linguagem natural.

### Consultas

Por exemplo, você pode pedir ao PandasAI para encontrar todas as linhas em um DataFrame onde o valor de uma coluna seja maior que 5, e ele retornará um DataFrame contendo apenas essas linhas:

```python
import pandas as pd
from pandasai import SmartDataframe

# Exemplo de DataFrame
df = pd.DataFrame({
    "country": ["United States", "United Kingdom", "France", "Germany", "Italy", "Spain", "Canada", "Australia", "Japan", "China"],
    "gdp": [19294482071552, 2891615567872, 2411255037952, 3435817336832, 1745433788416, 1181205135360, 1607402389504, 1490967855104, 4380756541440, 14631844184064],
    "happiness_index": [6.94, 7.16, 6.66, 7.07, 6.38, 6.4, 7.23, 7.22, 5.87, 5.12]
})

# Instanciando a LLM
from pandasai.llm import OpenAI
llm = OpenAI(api_token="YOUR_API_TOKEN")

df = SmartDataframe(df, config={"llm": llm})
df.chat('Which are the 5 happiest countries?')
```

O código acima retornará o seguinte:

```shell
6            Canada
7         Australia
1    United Kingdom
3           Germany
0     United States
Name: country, dtype: object
```

Claro, você também pode pedir ao PandasAI para realizar consultas mais complexas. Por exemplo, você pode perguntar ao PandasAI para encontrar a soma dos PIBs dos 2 países menos felizes:

```python
df.chat('What is the sum of the GDPs of the 2 unhappiest countries?')
```

O código acima retornará o seguinte:

```shell
19012600725504
```

### Gráficos

Você também pode pedir ao PandasAI para desenhar um gráfico:

```python
df.chat(
    "Plot the histogram of countries showing for each the gdp, using different colors for each bar",
)
```

![Chart](images/histogram-chart.png?raw=true)

Você pode salvar todos os gráficos gerados pelo PandasAI configurando o parâmetro `save_charts` como `True` no construtor do `PandasAI`. Por exemplo, `PandasAI(llm, save_charts=True)`. Os gráficos são salvos em `./pandasai/exports/charts`.

### Múltiplos DataFrames

Além disso, você também pode passar vários DataFrames para o PandasAI e fazer perguntas relacionadas a eles.

```python
import pandas as pd
from pandasai import SmartDatalake
from pandasai.llm import OpenAI

employees_data = {
    'EmployeeID': [1, 2, 3, 4, 5],
    'Name': ['John', 'Emma', 'Liam', 'Olivia', 'William'],
    'Department': ['HR', 'Sales', 'IT', 'Marketing', 'Finance']
}

salaries_data = {
    'EmployeeID': [1, 2, 3, 4, 5],
    'Salary': [5000, 6000, 4500, 7000, 5500]
}

employees_df = pd.DataFrame(employees_data)
salaries_df = pd.DataFrame(salaries_data)


llm = OpenAI()
dl = SmartDatalake([employees_df, salaries_df], config={"llm": llm})
dl.chat("Who gets paid the most?")
```

O código acima retornará o seguinte:

```console
Oh, Olivia gets paid the most.
```

Você pode encontrar mais exemplos no diretório de [exemplos](examples) directory.

### ⚡️ Atalhos

O PandasAI também fornece uma série de atalhos (beta) para facilitar a realização de perguntas aos seus dados. Por exemplo, você pode pedir ao PandasAI para limpar dados, manipular valores ausentes, gerar colunas novas e plotar histograma, respectivamente, com as funções `clean_data`, `impute_missing_values`, `generate_features`, `plot_histogram`, e muitas outras.

```python
# Limpeza de dados
df.clean_data()

# Imputação de valores ausentes
df.impute_missing_values()

# Geração de colunas para modelagem
df.generate_features()

# Plotar histograma
df.plot_histogram(column="gdp")
```

Saiba mais sobre os atalhos [aqui](https://pandas-ai.readthedocs.io/en/latest/shortcuts/).

## 🔒 Privacidade e Segurança

Para gerar o código Python a ser executado, pegamos a parte inicial do dataframe, fazemos uma randomização (usando geração aleatória para dados sensíveis e embaralhamento para dados não sensíveis) e enviamos apenas essa parte.

Além disso, se você deseja reforçar ainda mais sua privacidade, pode instanciar o PandasAI com `enforce_privacy = True`, o que não enviará a parte inicial (mas apenas os nomes das colunas) para o LLM.

## 🤝 Contributing

Contribuições são bem-vindas! Por favor, confira as tarefas pendentes abaixo e sinta-se à vontade para abrir um pull request.
Para obter mais informações, consulte as [diretrizes de contribuição](CONTRIBUTING.md).

Após instalar o ambiente virtual, lembre-se de instalar o `pre-commit` para estar em conformidade com nossos padrões:

```bash
pre-commit install
```

## Contribuidores

[![Contribuidores](https://contrib.rocks/image?repo=gventuri/pandas-ai)](https://github.com/gventuri/pandas-ai/graphs/contributors)

## 📜 Licença

O PandasAI está licenciado sob a Licença MIT. Consulte o arquivo LICENSE para obter mais detalhes.

## Agradecimentos

- Este projeto é baseado na biblioteca [pandas](https://github.com/pandas-dev/pandas) por contribuidores independentes, mas não tem afiliação nenhuma com o projeto pandas.
- Este projeto destina-se a ser usado como uma ferramenta para exploração e análise de dados, não sendo destinado a fins de produção. Por favor, use-o com responsabilidade.
