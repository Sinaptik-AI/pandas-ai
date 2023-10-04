from abc import ABC


class DataframeAbstract(ABC):
    _engine: str

    @property
    def dataframe(self):
        raise NotImplementedError("This method must be implemented in the child class")

    # Columns
    @property
    def columns(self) -> list:
        return self.dataframe.columns

    def rename(self, columns):
        """
        A proxy-call to the dataframe's `.rename()`.
        """
        return self.dataframe.rename(columns=columns)

    # Index
    @property
    def index(self):
        return self.dataframe.index

    def set_index(self, keys):
        """
        A proxy-call to the dataframe's `.set_index()`.
        """
        return self.dataframe.set_index(keys=keys)

    def reset_index(self, drop=False):
        """
        A proxy-call to the dataframe's `.reset_index()`.
        """
        return self.dataframe.reset_index(drop=drop)

    # Data
    def head(self, n):
        """
        A proxy-call to the dataframe's `.head()`.
        """
        return self.dataframe.head(n=n)

    def tail(self, n):
        """
        A proxy-call to the dataframe's `.tail()`.
        """
        return self.dataframe.tail(n=n)

    def sample(self, n):
        """
        A proxy-call to the dataframe's `.sample()`.
        """
        return self.dataframe.sample(n=n)

    def describe(self):
        """
        A proxy-call to the dataframe's `.describe()`.
        """
        return self.dataframe.describe()

    # Missing data
    def isna(self):
        """
        A proxy-call to the dataframe's `.isna()`.
        """
        return self.dataframe.isna()

    def notna(self):
        """
        A proxy-call to the dataframe's `.notna()`.
        """
        return self.dataframe.notna()

    def dropna(self, axis):
        """
        A proxy-call to the dataframe's `.dropna()`.
        """
        return self.dataframe.dropna(axis=axis)

    def fillna(self, value):
        """
        A proxy-call to the dataframe's `.fillna()`.
        """
        return self.dataframe.fillna(value=value)

    # Duplicates
    def duplicated(self):
        """
        A proxy-call to the dataframe's `.duplicated()`.
        """
        return self.dataframe.duplicated()

    def drop_duplicates(self, subset):
        """
        A proxy-call to the dataframe's `.drop_duplicates()`.
        """
        return self.dataframe.drop_duplicates(subset=subset)

    # Transform
    def apply(self, func):
        """
        A proxy-call to the dataframe's `.apply()`.
        """
        return self.dataframe.apply(func=func)

    def applymap(self, func):
        """
        A proxy-call to the dataframe's `.applymap()`.
        """
        return self.dataframe.applymap(func=func)

    def pipe(self, func):
        """
        A proxy-call to the dataframe's `.pipe()`.
        """
        return self.dataframe.pipe(func=func)

    # Groupby
    def groupby(self, by):
        """
        A proxy-call to the dataframe's `.groupby()`.
        """
        return self.dataframe.groupby(by=by)

    def pivot(self, index, columns, values):
        """
        A proxy-call to the dataframe's `.pivot()`.
        """
        return self.dataframe.pivot(index=index, columns=columns, values=values)

    def unstack(self):
        """
        A proxy-call to the dataframe's `.unstack()`.
        """
        return self.dataframe.unstack()

    # Join/Merge
    def append(self, other):
        """
        A proxy-call to the dataframe's `.append()`.
        """
        return self.dataframe.append(other=other)

    def join(self, other):
        """
        A proxy-call to the dataframe's `.join()`.
        """
        return self.dataframe.join(other=other)

    def merge(self, other):
        """
        A proxy-call to the dataframe's `.merge()`.
        """
        return self.dataframe.merge(other=other)

    # Combine
    def concat(self, others):
        """
        A proxy-call to the dataframe's `.concat()`.
        """
        return self.dataframe.concat(others=others)

    # Statistical
    def count(self):
        """
        A proxy-call to the dataframe's `.count()`.
        """
        return self.dataframe.count()

    def mean(self):
        """
        A proxy-call to the dataframe's `.mean()`.
        """
        return self.dataframe.mean()

    def median(self):
        """
        A proxy-call to the dataframe's `.median()`.
        """
        return self.dataframe.median()

    def std(self):
        """
        A proxy-call to the dataframe's `.std()`.
        """
        return self.dataframe.std()

    def min(self):
        """
        A proxy-call to the dataframe's `.min()`.
        """
        return self.dataframe.min()

    def max(self):
        """
        A proxy-call to the dataframe's `.max()`.
        """
        return self.dataframe.max()

    def abs(self):
        """
        A proxy-call to the dataframe's `.abs()`.
        """
        return self.dataframe.abs()

    def prod(self):
        """
        A proxy-call to the dataframe's `.prod()`.
        """
        return self.dataframe.prod()

    def sum(self):
        """
        A proxy-call to the dataframe's `.sum()`.
        """
        return self.dataframe.sum()

    def nunique(self):
        """
        A proxy-call to the dataframe's `.nunique()`.
        """
        return self.dataframe.nunique()

    def value_counts(self):
        """
        A proxy-call to the dataframe's `.value_counts()`.
        """
        return self.dataframe.value_counts()

    def corr(self):
        """
        A proxy-call to the dataframe's `.corr()`.
        """
        return self.dataframe.corr()

    def cov(self):
        """
        A proxy-call to the dataframe's `.cov()`.
        """
        return self.dataframe.cov()

    # Window
    def rolling(self, window):
        """
        A proxy-call to the dataframe's `.window()`.
        """
        return self.dataframe.rolling(window=window)

    def expanding(self, min_periods):
        """
        A proxy-call to the dataframe's `.expanding()`.
        """
        return self.dataframe.expanding(min_periods=min_periods)

    def resample(self, rule):
        """
        A proxy-call to the dataframe's `.resample()`.
        """
        return self.dataframe.resample(rule=rule)

    # Plotting
    def plot(self):
        """
        A proxy-call to the dataframe's `.plot()`.
        """
        return self.dataframe.plot()

    def hist(self):
        """
        A proxy-call to the dataframe's `.hist()`.
        """
        return self.dataframe.hist()

    # Exporting
    def to_csv(self, path):
        """
        A proxy-call to the dataframe's `.to_csv()`.
        """
        return self.dataframe.to_csv(path_or_buf=path)

    def to_json(self, path):
        """
        A proxy-call to the dataframe's `.to_json()`.
        """
        return self.dataframe.to_json(path=path)

    def to_sql(self, name, con):
        """
        A proxy-call to the dataframe's `.to_sql()`.
        """
        return self.dataframe.to_sql(name=name, con=con)

    def to_dict(self, orient="dict", into=dict, as_series=True):
        """
        A proxy-call to the dataframe's `.to_dict()`.
        """
        if self._engine == "pandas":
            return self.dataframe.to_dict(orient=orient, into=into)
        elif self._engine == "polars":
            return self.dataframe.to_dict(as_series=as_series)
        raise RuntimeError(
            f"{self.__class__} object has unknown engine type. "
            f"Possible engines: 'pandas', 'polars'. Actual '{self._engine}'."
        )

    def to_numpy(self):
        """
        A proxy-call to the dataframe's `.to_numpy()`.
        """
        return self.dataframe.to_numpy()

    def to_markdown(self):
        """
        A proxy-call to the dataframe's `.to_markdown()`.
        """
        return self.dataframe.to_markdown()

    def to_parquet(self):
        """
        A proxy-call to the dataframe's `.to_parquet()`.
        """
        return self.dataframe.to_parquet()

    # Query
    def query(self, expr):
        """
        A proxy-call to the dataframe's `.query()`.
        """
        return self.dataframe.query(expr=expr)

    def filter(self, expr):
        """
        A proxy-call to the dataframe's `.filter()`.
        """
        return self.dataframe.filter(items=expr)
