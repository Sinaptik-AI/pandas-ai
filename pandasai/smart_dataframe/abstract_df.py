from abc import ABC


class DataframeAbstract(ABC):
    # Columns
    @property
    def columns(self) -> list:
        return self.dataframe_proxy.columns

    def rename(self, columns):
        """
        A proxy-call to the dataframe's `.rename()`.
        """
        return self.dataframe_proxy.rename(columns=columns)

    # Index
    @property
    def index(self):
        return self.dataframe_proxy.index

    def set_index(self, keys):
        """
        A proxy-call to the dataframe's `.set_index()`.
        """
        return self.dataframe_proxy.set_index(keys=keys)

    def reset_index(self, drop=False):
        """
        A proxy-call to the dataframe's `.reset_index()`.
        """
        return self.dataframe_proxy.reset_index(drop=drop)

    # Data
    def head(self, n):
        """
        A proxy-call to the dataframe's `.head()`.
        """
        return self.dataframe_proxy.head(n=n)

    def tail(self, n):
        """
        A proxy-call to the dataframe's `.tail()`.
        """
        return self.dataframe_proxy.tail(n=n)

    def sample(self, n):
        """
        A proxy-call to the dataframe's `.sample()`.
        """
        return self.dataframe_proxy.sample(n=n)

    def describe(self):
        """
        A proxy-call to the dataframe's `.describe()`.
        """
        return self.dataframe_proxy.describe()

    # Missing data
    def isna(self):
        """
        A proxy-call to the dataframe's `.isna()`.
        """
        return self.dataframe_proxy.isna()

    def notna(self):
        """
        A proxy-call to the dataframe's `.notna()`.
        """
        return self.dataframe_proxy.notna()

    def dropna(self, axis):
        """
        A proxy-call to the dataframe's `.dropna()`.
        """
        return self.dataframe_proxy.dropna(axis=axis)

    def fillna(self, value):
        """
        A proxy-call to the dataframe's `.fillna()`.
        """
        return self.dataframe_proxy.fillna(value=value)

    # Duplicates
    def duplicated(self):
        """
        A proxy-call to the dataframe's `.duplicated()`.
        """
        return self.dataframe_proxy.duplicated()

    def drop_duplicates(self, subset):
        """
        A proxy-call to the dataframe's `.drop_duplicates()`.
        """
        return self.dataframe_proxy.drop_duplicates(subset=subset)

    # Transform
    def apply(self, func):
        """
        A proxy-call to the dataframe's `.apply()`.
        """
        return self.dataframe_proxy.apply(func=func)

    def applymap(self, func):
        """
        A proxy-call to the dataframe's `.applymap()`.
        """
        return self.dataframe_proxy.applymap(func=func)

    def pipe(self, func):
        """
        A proxy-call to the dataframe's `.pipe()`.
        """
        return self.dataframe_proxy.pipe(func=func)

    # Groupby
    def groupby(self, by):
        """
        A proxy-call to the dataframe's `.groupby()`.
        """
        return self.dataframe_proxy.groupby(by=by)

    def pivot(self, index, columns, values):
        """
        A proxy-call to the dataframe's `.pivot()`.
        """
        return self.dataframe_proxy.pivot(index=index, columns=columns, values=values)

    def unstack(self):
        """
        A proxy-call to the dataframe's `.unstack()`.
        """
        return self.dataframe_proxy.unstack()

    # Join/Merge
    def append(self, other):
        """
        A proxy-call to the dataframe's `.append()`.
        """
        return self.dataframe_proxy.append(other=other)

    def join(self, other):
        """
        A proxy-call to the dataframe's `.join()`.
        """
        return self.dataframe_proxy.join(other=other)

    def merge(self, other):
        """
        A proxy-call to the dataframe's `.merge()`.
        """
        return self.dataframe_proxy.merge(other=other)

    # Combine
    def concat(self, others):
        """
        A proxy-call to the dataframe's `.concat()`.
        """
        return self.dataframe_proxy.concat(others=others)

    # Statistical
    def count(self):
        """
        A proxy-call to the dataframe's `.count()`.
        """
        return self.dataframe_proxy.count()

    def mean(self):
        """
        A proxy-call to the dataframe's `.mean()`.
        """
        return self.dataframe_proxy.mean()

    def median(self):
        """
        A proxy-call to the dataframe's `.median()`.
        """
        return self.dataframe_proxy.median()

    def std(self):
        """
        A proxy-call to the dataframe's `.std()`.
        """
        return self.dataframe_proxy.std()

    def min(self):
        """
        A proxy-call to the dataframe's `.min()`.
        """
        return self.dataframe_proxy.min()

    def max(self):
        """
        A proxy-call to the dataframe's `.max()`.
        """
        return self.dataframe_proxy.max()

    def abs(self):
        """
        A proxy-call to the dataframe's `.abs()`.
        """
        return self.dataframe_proxy.abs()

    def prod(self):
        """
        A proxy-call to the dataframe's `.prod()`.
        """
        return self.dataframe_proxy.prod()

    def sum(self):
        """
        A proxy-call to the dataframe's `.sum()`.
        """
        return self.dataframe_proxy.sum()

    def nunique(self):
        """
        A proxy-call to the dataframe's `.nunique()`.
        """
        return self.dataframe_proxy.nunique()

    def value_counts(self):
        """
        A proxy-call to the dataframe's `.value_counts()`.
        """
        return self.dataframe_proxy.value_counts()

    def corr(self):
        """
        A proxy-call to the dataframe's `.corr()`.
        """
        return self.dataframe_proxy.corr()

    def cov(self):
        """
        A proxy-call to the dataframe's `.cov()`.
        """
        return self.dataframe_proxy.cov()

    # Window
    def rolling(self, window):
        """
        A proxy-call to the dataframe's `.window()`.
        """
        return self.dataframe_proxy.rolling(window=window)

    def expanding(self, min_periods):
        """
        A proxy-call to the dataframe's `.expanding()`.
        """
        return self.dataframe_proxy.expanding(min_periods=min_periods)

    def resample(self, rule):
        """
        A proxy-call to the dataframe's `.resample()`.
        """
        return self.dataframe_proxy.resample(rule=rule)

    # Plotting
    def plot(self):
        """
        A proxy-call to the dataframe's `.plot()`.
        """
        return self.dataframe_proxy.plot()

    def hist(self):
        """
        A proxy-call to the dataframe's `.hist()`.
        """
        return self.dataframe_proxy.hist()

    # Exporting
    def to_csv(self, path):
        """
        A proxy-call to the dataframe's `.to_csv()`.
        """
        return self.dataframe_proxy.to_csv(path_or_buf=path)

    def to_json(self, path):
        """
        A proxy-call to the dataframe's `.to_json()`.
        """
        return self.dataframe_proxy.to_json(path=path)

    def to_sql(self, name, con):
        """
        A proxy-call to the dataframe's `.to_sql()`.
        """
        return self.dataframe_proxy.to_sql(name=name, con=con)

    def to_dict(self, orient="dict", into=dict):
        """
        A proxy-call to the dataframe's `.to_dict()`.
        """
        return self.dataframe_proxy.to_dict(orient=orient, into=into)

    def to_numpy(self):
        """
        A proxy-call to the dataframe's `.to_numpy()`.
        """
        return self.dataframe_proxy.to_numpy()

    def to_markdown(self):
        """
        A proxy-call to the dataframe's `.to_markdown()`.
        """
        return self.dataframe_proxy.to_markdown()

    def to_parquet(self):
        """
        A proxy-call to the dataframe's `.to_parquet()`.
        """
        return self.dataframe_proxy.to_parquet()

    # Query
    def query(self, expr):
        """
        A proxy-call to the dataframe's `.query()`.
        """
        return self.dataframe_proxy.query(expr=expr)

    def filter(self, expr):
        """
        A proxy-call to the dataframe's `.filter()`.
        """
        return self.dataframe_proxy.filter(items=expr)
