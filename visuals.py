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



def bar_chart(months, cost, revenue, cashflow, no_of_actual_months):
    color_for_revenue = 'rgba(0, 159, 183, 0.8)'
    color_for_revenue_shaded = 'rgba(0, 159, 183, 0.4)'
    color_for_cost = 'rgba(230, 95, 92, 0.8)'
    color_for_cost_shaded = 'rgba(230, 95, 92, 0.4)'
    colors_revenue = [color_for_revenue,] * len(months)
    colors_cost = [color_for_cost,] * len(months)
    for i in range(no_of_actual_months):
        colors_revenue[i] = color_for_revenue_shaded
    for i in range(no_of_actual_months):
        colors_cost[i] = color_for_cost_shaded

    fig = go.Figure(data=[
        go.Bar(name= 'Cost', x=months, y=cost, marker_color = colors_cost),
        go.Bar(name= 'Revenue', x=months, y=revenue, marker_color = colors_revenue),
        ])
    fig.add_trace(go.Line(name= 'Cashflow', x=months, y=cashflow, marker_color = 'rgb(14, 52, 160)'))

    fig.update_layout(
        barmode='group',
        yaxis=dict(title='Amount, $'),
        xaxis_tickangle=0,
        # title_text='Cashflow graph',
        legend=dict(
            x=0.84,
            y=1.2,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)',
            orientation='h',
            ),
        width=1630,
        height=200,
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=0
            )
        )

    return fig
