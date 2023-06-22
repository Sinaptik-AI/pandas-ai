# Shortcuts

Shortcuts are a way to quickly access the most common queries. At the moment, shortcuts are in beta, and only a few are available. More will be added in the future.

## Available shortcuts

### clean_data

```python
df = pd.read_csv('data.csv')
pandas_ai.clean_data(df)
```

This shortcut will do data cleaning on the data frame.

### impute_missing_values

```python
df = pd.read_csv('data.csv')
pandas_ai.impute_missing_values(df)
```

This shortcut will impute missing values in the data frame.

### generate_features

```python
df = pd.read_csv('data.csv')
pandas_ai.generate_features(df)
```

This shortcut will generate features in the data frame.

### plot_pie_chart

```python
df = pd.read_csv('data.csv')
pandas_ai.plot_pie_chart(df, labels = ['a', 'b', 'c'], values = [1, 2, 3])
```

This shortcut will plot a pie chart of the data frame.

### plot_bar_chart

```python
df = pd.read_csv('data.csv')
pandas_ai.plot_bar_chart(df, x = ['a', 'b', 'c'], y = [1, 2, 3])
```

This shortcut will plot a bar chart of the data frame.

### plot_bar_chart

```python
df = pd.read_csv('data.csv')
pandas_ai.plot_bar_chart(df, x = ['a', 'b', 'c'])
```

This shortcut will plot a bar chart of the data frame.

### plot_histogram

```python
df = pd.read_csv('data.csv')
pandas_ai.plot_histogram(df, column = 'a')
```

This shortcut will plot a histogram of the data frame.

### plot_line_chart

```python
df = pd.read_csv('data.csv')
pandas_ai.plot_line_chart(df, x = ['a', 'b', 'c'], y = [1, 2, 3])
```

This shortcut will plot a line chart of the data frame.

### plot_scatter_chart

```python
df = pd.read_csv('data.csv')
pandas_ai.plot_scatter_chart(df, x = ['a', 'b', 'c'], y = [1, 2, 3])
```

This shortcut will plot a scatter chart of the data frame.

### plot_correlation_heatmap

```python
df = pd.read_csv('data.csv')
pandas_ai.plot_correlation_heatmap(df)
```

This shortcut will plot a correlation heatmap of the data frame.

### plot_confusion_matrix

```python
df = pd.read_csv('data.csv')
pandas_ai.plot_confusion_matrix(df, y_true = [1, 2, 3], y_pred = [1, 2, 3])
```

This shortcut will plot a confusion matrix of the data frame.

### plot_roc_curve

```python
df = pd.read_csv('data.csv')
pandas_ai.plot_roc_curve(df, y_true = [1, 2, 3], y_pred = [1, 2, 3])
```

This shortcut will plot a ROC curve of the data frame.

### rolling_mean

```python
df = pd.read_csv('data.csv')
pandas_ai.rolling_mean(df, column = 'a', window = 5)
```

This shortcut will calculate the rolling mean of the data frame.

### rolling_median

```python
df = pd.read_csv('data.csv')
pandas_ai.rolling_median(df, column = 'a', window = 5)
```

This shortcut will calculate the rolling median of the data frame.

### rolling_std

```python
df = pd.read_csv('data.csv')
pandas_ai.rolling_std(df, column = 'a', window = 5)
```

This shortcut will calculate the rolling standard deviation of the data frame.

### segment_customers

```python
df = pd.read_csv('data.csv')
pandas_ai.segment_customers(df, features = ['a', 'b', 'c'], n_clusters = 5)
```

This shortcut will segment customers in the data frame.
