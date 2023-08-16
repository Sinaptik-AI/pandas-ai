from abc import ABC


class DataframeAbstract(ABC):
    @property
    def dataframe(self):
        raise NotImplementedError("This method must be implemented in the child class")

    # Columns
    @property
    def columns(self) -> list:
        return self.dataframe.columns

    def rename(self, columns):
        return self.dataframe.rename(columns=columns)

    # Index
    @property
    def index(self):
        return self.dataframe.index

    def set_index(self, keys):
        return self.dataframe.set_index(keys=keys)

    def reset_index(self, drop=False):
        return self.dataframe.reset_index(drop=drop)

    # Data
    def head(self, n):
        return self.dataframe.head(n=n)

    def tail(self, n):
        return self.dataframe.tail(n=n)

    def sample(self, n):
        return self.dataframe.sample(n=n)

    def describe(self):
        return self.dataframe.describe()

    # Missing data
    def isna(self):
        return self.dataframe.isna()

    def notna(self):
        return self.dataframe.notna()

    def dropna(self, axis):
        return self.dataframe.dropna(axis=axis)

    def fillna(self, value):
        return self.dataframe.fillna(value=value)

    # Duplicates
    def duplicated(self):
        return self.dataframe.duplicated()

    def drop_duplicates(self, subset):
        return self.dataframe.drop_duplicates(subset=subset)

    # Transform
    def apply(self, func):
        return self.dataframe.apply(func=func)

    def applymap(self, func):
        return self.dataframe.applymap(func=func)

    def pipe(self, func):
        return self.dataframe.pipe(func=func)

    # Groupby
    def groupby(self, by):
        return self.dataframe.groupby(by=by)

    def pivot(self, index, columns, values):
        return self.dataframe.pivot(index=index, columns=columns, values=values)

    def unstack(self):
        return self.dataframe.unstack()

    # Join/Merge
    def append(self, other):
        return self.dataframe.append(other=other)

    def join(self, other):
        return self.dataframe.join(other=other)

    def merge(self, other):
        return self.dataframe.merge(other=other)

    # Combine
    def concat(self, others):
        return self.dataframe.concat(others=others)

    # Statistical
    def count(self):
        return self.dataframe.count()

    def mean(self):
        return self.dataframe.mean()

    def median(self):
        return self.dataframe.median()

    def std(self):
        return self.dataframe.std()

    def min(self):
        return self.dataframe.min()

    def max(self):
        return self.dataframe.max()

    def abs(self):
        return self.dataframe.abs()

    def prod(self):
        return self.dataframe.prod()

    def sum(self):
        return self.dataframe.sum()

    def nunique(self):
        return self.dataframe.nunique()

    def value_counts(self):
        return self.dataframe.value_counts()

    def corr(self):
        return self.dataframe.corr()

    def cov(self):
        return self.dataframe.cov()

    # Window
    def rolling(self, window):
        return self.dataframe.rolling(window=window)

    def expanding(self, min_periods):
        return self.dataframe.expanding(min_periods=min_periods)

    def resample(self, rule):
        return self.dataframe.resample(rule=rule)

    # Plotting
    def plot(self):
        return self.dataframe.plot()

    def hist(self):
        return self.dataframe.hist()

    # Exporting
    def to_csv(self, path):
        return self.dataframe.to_csv(path=path)

    def to_json(self, path):
        return self.dataframe.to_json(path=path)

    def to_sql(self, name, con):
        return self.dataframe.to_sql(name=name, con=con)

    def to_dict(self, orient):
        return self.dataframe.to_dict(orient=orient)

    def to_numpy(self):
        return self.dataframe.to_numpy()

    def to_markdown(self):
        return self.dataframe.to_markdown()

    # Query
    def query(self, expr):
        return self.dataframe.query(expr=expr)

    def filter(self, expr):
        return self.dataframe.filter(items=expr)
