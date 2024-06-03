## PandasAI Server

## Run

### Prerequisites

- Make sure postgres is already installed
- Create an env file use .env.example

### Install dependency

```shell
> poetry shell
> make install
```

### Apply database migration

```shell
> make migrate
```

### Create new database migration after schema changes

```shell
> make generate-migration
```

### Start Server

```shell
> make start
```
