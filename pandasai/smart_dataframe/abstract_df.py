class DataframeAbstract:
    # Columns
    @property
    def columns(self) -> list:
        raise NotImplementedError

    def rename(self, columns):
        raise NotImplementedError

    # Index
    @property
    def index(self):
        raise NotImplementedError

    def set_index(self, keys):
        raise NotImplementedError

    def reset_index(self, drop=False):
        raise NotImplementedError

    # Data
    def head(self, n):
        raise NotImplementedError

    def tail(self, n):
        raise NotImplementedError

    def sample(self, n):
        raise NotImplementedError

    def describe(self):
        raise NotImplementedError

    # Missing data
    def isna(self):
        raise NotImplementedError

    def notna(self):
        raise NotImplementedError

    def dropna(self, axis):
        raise NotImplementedError

    def fillna(self, value):
        raise NotImplementedError

    # Duplicates
    def duplicated(self):
        raise NotImplementedError

    def drop_duplicates(self, subset):
        raise NotImplementedError

    # Transform
    def apply(self, func):
        raise NotImplementedError

    def applymap(self, func):
        raise NotImplementedError

    def pipe(self, func):
        raise NotImplementedError

    # Groupby
    def groupby(self, by):
        raise NotImplementedError

    def pivot(self, index, columns, values):
        raise NotImplementedError

    def unstack(self):
        raise NotImplementedError

    # Join/Merge
    def append(self, other):
        raise NotImplementedError

    def join(self, other):
        raise NotImplementedError

    def merge(self, other):
        raise NotImplementedError

    # Combine
    def concat(self, others):
        raise NotImplementedError

    # Statistical
    def count(self):
        raise NotImplementedError

    def mean(self):
        raise NotImplementedError

    def median(self):
        raise NotImplementedError

    def std(self):
        raise NotImplementedError

    def min(self):
        raise NotImplementedError

    def max(self):
        raise NotImplementedError

    def abs(self):
        raise NotImplementedError

    def prod(self):
        raise NotImplementedError

    def sum(self):
        raise NotImplementedError

    def nunique(self):
        raise NotImplementedError

    def value_counts(self):
        raise NotImplementedError

    def corr(self):
        raise NotImplementedError

    def cov(self):
        raise NotImplementedError

    # Window
    def rolling(self, window):
        raise NotImplementedError

    def expanding(self, min_periods):
        raise NotImplementedError

    def resample(self, rule):
        raise NotImplementedError

    # Plotting
    def plot(self):
        raise NotImplementedError

    def hist(self):
        raise NotImplementedError

    # Exporting
    def to_csv(self, path):
        raise NotImplementedError

    def to_json(self, path):
        raise NotImplementedError

    def to_sql(self, name, con):
        raise NotImplementedError

    def to_dict(self, orient):
        raise NotImplementedError

    def to_numpy(self):
        raise NotImplementedError

    def to_markdown(self):
        raise NotImplementedError

    # Query
    def query(self, expr):
        raise NotImplementedError

    def filter(self, expr):
        raise NotImplementedError
