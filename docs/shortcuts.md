# Shortcuts

Shortcuts are a way to quickly access the most common queries. At the moment, shortcuts are in beta, and only a few are available. More will be added in the future.

## Available shortcuts

### clean_data

```python
df = SmartDataframe('data.csv')
df.clean_data()
```

This shortcut will do data cleaning on the data frame.

### impute_missing_values

```python
df = SmartDataframe('data.csv')
df.impute_missing_values()
```

This shortcut will impute missing values in the data frame.

### generate_features

```python
df = SmartDataframe('data.csv')
df.generate_features()
```

This shortcut will generate features in the data frame.

### plot_pie_chart

```python
df = SmartDataframe('data.csv')
df.plot_pie_chart(labels = ['a', 'b', 'c'], values = [1, 2, 3])
```

This shortcut will plot a pie chart of the data frame.

### plot_bar_chart

```python
df = SmartDataframe('data.csv')
df.plot_bar_chart(x = ['a', 'b', 'c'], y = [1, 2, 3])
```

This shortcut will plot a bar chart of the data frame.

### plot_histogram

```python
df = SmartDataframe('data.csv')
df.plot_histogram(column = 'a')
```

This shortcut will plot a histogram of the data frame.

### plot_line_chart

```python
df = SmartDataframe('data.csv')
df.plot_line_chart(x = ['a', 'b', 'c'], y = [1, 2, 3])
```

This shortcut will plot a line chart of the data frame.

### plot_scatter_chart

```python
df = SmartDataframe('data.csv')
df.plot_scatter_chart(x = ['a', 'b', 'c'], y = [1, 2, 3])
```

This shortcut will plot a scatter chart of the data frame.

### plot_correlation_heatmap

```python
df = SmartDataframe('data.csv')
df.plot_correlation_heatmap(df)
```

This shortcut will plot a correlation heatmap of the data frame.

### plot_confusion_matrix

```python
df = SmartDataframe('data.csv')
df.plot_confusion_matrix(y_true = [1, 2, 3], y_pred = [1, 2, 3])
```

This shortcut will plot a confusion matrix of the data frame.

### plot_roc_curve

```python
df = SmartDataframe('data.csv')
df.plot_roc_curve(y_true = [1, 2, 3], y_pred = [1, 2, 3])
```

This shortcut will plot a ROC curve of the data frame.

### boxplot

```python
df = SmartDataframe('data.csv')
df.boxplot(col='A', by='B', style='Highlight outliers with a x')
```

This shortcut plots a box-and-whisker plot using the DataFrame `df`, focusing on the `'A'` column and grouping the data by the `'B'` column.

The `style` parameter allows users to communicate their desired plot customizations to the Language Model, providing flexibility for further refinement and adaptability to specific visual requirements.

### rolling_mean

```python
df = SmartDataframe('data.csv')
df.rolling_mean(column = 'a', window = 5)
```

This shortcut will calculate the rolling mean of the data frame.

### rolling_median

```python
df = SmartDataframe('data.csv')
df.rolling_median(column = 'a', window = 5)
```

This shortcut will calculate the rolling median of the data frame.

### rolling_std

```python
df = SmartDataframe('data.csv')
df.rolling_std(column = 'a', window = 5)
```

This shortcut will calculate the rolling standard deviation of the data frame.

### segment_customers

```python
df = SmartDataframe('data.csv')
df.segment_customers(features = ['a', 'b', 'c'], n_clusters = 5)
```

This shortcut will segment customers in the data frame.
