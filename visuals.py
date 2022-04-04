import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def gantt_chart():
    gantt_df = pd.DataFrame([
        dict(Cost_Item="Cost Item 110", Start='2022-01-01', Finish='2022-02-28', complete=50),
        dict(Cost_Item="Cost Item 120", Start='2022-02-01', Finish='2022-04-15', complete=35),
        dict(Cost_Item="Cost Item 230", Start='2022-01-20', Finish='2022-05-3', complete=70),
        dict(Cost_Item="Cost Item 250", Start='2022-01-01', Finish='2022-03-15', complete=20),
        dict(Cost_Item="Cost Item 325", Start='2022-02-01', Finish='2022-06-15', complete=45),
        dict(Cost_Item="Cost Item 410", Start='2022-01-20', Finish='2022-05-3', complete=90)
    ])

    fig = px.timeline(gantt_df, x_start="Start", x_end="Finish", y="Cost_Item", color='complete')
    fig.update_yaxes(autorange="reversed") # otherwise tasks are listed from the bottom up
    fig.update_layout(
            width=1600,
            height=200,
            margin=dict(
                l=1,
                r=0,
                b=0,
                t=1
                )
            )
    return fig

def bar_chart():
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
    y1 = [43,34,32,42,34,32,46,34,32,52,48,35]
    y2 = [41,35,41,51,35,41,48,35,41,45,34,32]
    fig = go.Figure(data=[
        go.Bar(name= 'Costs', x=months, y=y1, marker_color = 'rgba(50,80,50,0.7)'),
        go.Bar(name= 'Revenue', x=months, y=y2)
        ])
    fig.update_layout(
        barmode='group',
        xaxis_tickangle=0,
        # title_text='Cashflow graph',
        legend=dict(
            x=0.0,
            y=1.4,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
            ),
        width=1560,
        height=200,
        margin=dict(
            l=1,
            r=0,
            b=0,
            t=50
            )
        )

    return fig
