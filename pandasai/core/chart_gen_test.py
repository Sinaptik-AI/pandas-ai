import sys
import matplotlib.pyplot as plot
import pandas as pd


from generate_chart import generate_chart


if __name__ == '__main__':
    args=sys.argv[1:]
    library=args[0]
    chart_type=args[1]

    chart_object=None

    stacked_chart_df=pd.DataFrame({'gold':[24,10,9], 
                            'silver':[13,15,12],
                            'bronze':[11,8,12]}, index=['South Korea', 'China', 'Canada'])

    other_chart_df=pd.DataFrame({'nation':['South Korea', 'China', 'Canada', 'South Korea', 'China', 'Canada', 'South Korea', 'China', 'Canada'], 
                    'medal':['gold', 'gold', 'gold', 'silver', 'silver', 'silver', 'bronze', 'bronze', 'bronze'],
                    'count': [24, 10, 9, 13, 15, 12, 11, 8, 12]})
    
    library_chart_type_invocation_map={
        "matplotlib":{
            "stacked_bar": {"df": stacked_chart_df, "chart_type": "bar", "other_args" : {"x": 'nation', "y": 'count', "stacked": True, "title": "Medal count"}},
            "bar": {"df": other_chart_df, "chart_type": "bar", "other_args" : {"x": 'nation', "y": 'count', "title": "Medal count"}},
            "line": {"df": other_chart_df, "chart_type": "line", "other_args" : {"x": 'nation', "y": 'count', "color": "red", "title": "Medal count"}},
            "scatter": {"df": other_chart_df, "chart_type": "scatter", "other_args" : {"x": 'nation', "y": 'count', "color": "green", "title": "Medal count"}}
        },
        "plotly":{
            "stacked_bar": {"df": other_chart_df, "chart_type": "bar", "other_args" : {"x": 'nation', "y": 'count', "color": "medal", "title": "Medal count"}},
            "bar": {"df": other_chart_df, "chart_type": "bar", "other_args" : {"x": 'nation', "y": 'count', "title": "Medal count"}},
            "line": {"df": other_chart_df, "chart_type": "line", "other_args" : {"x": 'nation', "y": 'count', "title": "Medal count"}},
            "scatter": {"df": other_chart_df, "chart_type": "scatter", "other_args" : {"x": 'nation', "y": 'count', "title": "Medal count"}}
        }
    }

    if library in library_chart_type_invocation_map:
        if chart_type in library_chart_type_invocation_map[library]:
            library_chart_config=library_chart_type_invocation_map[library][chart_type]
            target_df=library_chart_config['df']
            chart_type=library_chart_config['chart_type']
            other_args=library_chart_config['other_args']

            chart_object=generate_chart(target_df, library, chart_type, **other_args)
        else:
            print(library + "'s chart type " + chart_type + " is not included yet")
    else:
        print(library + " is not supported yet")


    if library == "matplotlib":
        plot.show()
    elif library == "plotly":
        if chart_object:
            chart_object.show()
    