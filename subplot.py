import json
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import pandas_ta as ta
from datetime import datetime
from plotly.subplots import make_subplots
import plotly.graph_objects as go


pd.options.mode.chained_assignment = None


def get_data(timeframe):
    data = requests.get('https://data.tradeui.com/dt.php?symbol=FB&tf='+timeframe).text

    soup = BeautifulSoup(data)

    json_data = soup.pre.text.strip('" ')
    res = json.loads(json_data)
    df = pd.DataFrame.from_dict(pd.json_normalize(res['\x00*\x00response']['bars']))
    symbol = res['\x00*\x00response']['symbol']
    return df,symbol


df,symbol = get_data("1Hour")
df_1_min,symbol = get_data("1Min")
df_5_min,symbol = get_data("5Min")
df_15_min,symbol = get_data("15Min")
df_1_day,symbol = get_data("1Day")
df_wz = df_1_day[df_1_day.vw != 0]


for i in range(len(df_1_day)):
    if df_1_day['vw'][i] == 0:
        df_1_day['vw'][i] = df_wz['vw'].mean()
    if df_1_day['v'][i] == 0:
        df_1_day['v'][i] = df_wz['v'].mean()



ratios = [0,0.236, 0.382, 0.5 , 0.618, 0.786,1]
def fibonacci_levels(data):
    highest_swing = -1
    lowest_swing = -1
    for i in range(1,data.shape[0]-1):
        if data['h'][i] > data['h'][i-1] and data['h'][i] > data['h'][i+1] and (highest_swing == -1 or data['h'][i] > data['h'][highest_swing]):
            highest_swing = i
        if data['l'][i] < data['l'][i-1] and data['l'][i] < data['l'][i+1] and (lowest_swing == -1 or data['l'][i] < data['l'][lowest_swing]):
            lowest_swing = i

    levels = []
    max_level = data['h'][highest_swing]
    min_level = data['h'][lowest_swing]
    for ratio in ratios:
        if highest_swing > lowest_swing:
            levels.append(max_level - (max_level-min_level)*ratio)
        else:
            levels.append(min_level + (max_level-min_level)*ratio)
    return levels


def get_shapes(data):
    shapes = []

    for i in range(len(fibonacci_levels(data))):
        shapes_dict = {'line':{'color':'yellow','dash':'dash','width':1},
                    'type':'line',
                    'x0':0,
                    'x1':1,
                    'xref':'x2 domain',
                    'y0':fibonacci_levels(data)[i],
                    'y1':fibonacci_levels(data)[i],
                    'yref':'y2'}
        shapes.append(shapes_dict)

    return shapes

def get_annotations(data):
    annotation = []
    for i in range(len(fibonacci_levels(data))):
        annotation_dict = {'showarrow':False,
                           'text':'{:.1f}%'.format(ratios[i]*100),
                           'x':1,
                           'xanchor':'right',
                           'xref':'x2 domain',
                           'y':fibonacci_levels(data)[i],
                           'yanchor':'bottom',
                           'yref':'y2'}
        annotation.append(annotation_dict)
    return annotation



df.ta.sma(close='c', length=50, append=True)
df.ta.sma(close='c', length=200, append=True)

df_1_min.ta.sma(close='c', length=50, append=True)
df_1_min.ta.sma(close='c', length=200, append=True)

df_5_min.ta.sma(close='c', length=50, append=True)
df_5_min.ta.sma(close='c', length=200, append=True)

df_15_min.ta.sma(close='c', length=50, append=True)
df_15_min.ta.sma(close='c', length=200, append=True)

df_1_day.ta.sma(close='c', length=50, append=True)
df_1_day.ta.sma(close='c', length=200, append=True)



fig = make_subplots(
    rows=2, cols=2,
    specs=[[{}, {}],
           [{"colspan": 2}, None]],
    vertical_spacing=0.03,
    row_width=[0.2, 0.7]
    )



fig.add_trace(go.Bar(
            x=df['v'],
            y=df['vw'],
            showlegend=False,
            visible=True,
            marker_color = "rgb(73,76,100)",
            marker_line_color='rgb(73,76,100)',
            yaxis='y1',
            xaxis='x1',
            opacity=0.7,
            orientation='h',
            width=1
            ),row=1, col=1)
fig.add_trace(go.Bar(
            x=df_1_min['v'],
            y=df_1_min['vw'],
            showlegend=False,
            visible=False,
            marker_color = "rgb(73,76,100)",
            marker_line_color='rgb(73,76,100)',
            yaxis='y8',
            xaxis='x8',
            opacity=0.7,
            orientation='h',
            width=1
            ),row=1, col=1)

fig.add_trace(go.Bar(
            x=df_5_min['v'],
            y=df_5_min['vw'],
            showlegend=False,
            visible=False,
            marker_color = "rgb(73,76,100)",
            marker_line_color='rgb(73,76,100)',
            yaxis='y9',
            xaxis='x9',
            opacity=0.7,
            orientation='h',
            width=1
            ),row=1, col=1)

fig.add_trace(go.Bar(
            x=df_15_min['v'],
            y=df_15_min['vw'],
            showlegend=False,
            visible=False,
            marker_color = "rgb(73,76,100)",
            marker_line_color='rgb(73,76,100)',
            yaxis='y10',
            xaxis='x10',
            opacity=0.7,
            orientation='h',
            width=1
            ),row=1, col=1)

fig.add_trace(go.Bar(
            x=df_1_day['v'],
            y=df_1_day['vw'],
            showlegend=False,
            visible=False,
            marker_color = "rgb(73,76,100)",
            marker_line_color='rgb(73,76,100)',
            yaxis='y11',
            xaxis='x11',
            opacity=0.7,
            orientation='h',
            width=1
            ),row=1, col=1)


fig.add_trace(go.Candlestick(
    x=df["t"],
    open=df['o'],
    high=df['h'],
    low=df['l'],
    close=df['c'],
    showlegend=False,
    yaxis='y2',
    xaxis='x2',
    increasing_line_color = "rgb(12,189,113)",
    decreasing_line_color = "rgb(249,74,74)"
    ),row=1, col=2)

fig.add_trace(go.Candlestick(
    x=df_1_min["t"],
    open=df_1_min['o'],
    high=df_1_min['h'],
    low=df_1_min['l'],
    close=df_1_min['c'],
    showlegend=False,
    yaxis='y4',
    xaxis='x4',
    visible=False,
    increasing_line_color = "rgb(12,189,113)",
    decreasing_line_color = "rgb(249,74,74)"
    ),row=1, col=2)

fig.add_trace(go.Candlestick(
    x=df_5_min["t"],
    open=df_5_min['o'],
    high=df_5_min['h'],
    low=df_5_min['l'],
    close=df_5_min['c'],
    showlegend=False,
    yaxis='y5',
    xaxis='x5',
    visible=False,
    increasing_line_color = "rgb(12,189,113)",
    decreasing_line_color = "rgb(249,74,74)"
    ),row=1, col=2)

fig.add_trace(go.Candlestick(
    x=df_15_min["t"],
    open=df_15_min['o'],
    high=df_15_min['h'],
    low=df_15_min['l'],
    close=df_15_min['c'],
    showlegend=False,
    yaxis='y6',
    xaxis='x6',
    visible=False,
    increasing_line_color = "rgb(12,189,113)",
    decreasing_line_color = "rgb(249,74,74)"
    ),row=1, col=2)

fig.add_trace(go.Candlestick(
    x=df_1_day["t"],
    open=df_1_day['o'],
    high=df_1_day['h'],
    low=df_1_day['l'],
    close=df_1_day['c'],
    showlegend=False,
    yaxis='y7',
    xaxis='x7',
    visible=False,
    increasing_line_color = "rgb(12,189,113)",
    decreasing_line_color = "rgb(249,74,74)"
    ),row=1, col=2)



fig.add_trace(
    go.Scatter(
        x=df["t"],
        y=df['SMA_50'],
        line=dict(color='rgb(95,104,192)', width=1),
        name='SMA_50',
        showlegend=False,
    ),row=1, col=2
)

fig.add_trace(
    go.Scatter(
        x=df_1_min["t"],
        y=df_1_min['SMA_50'],
        line=dict(color='rgb(95,104,192)', width=1),
        name='SMA_50',
        visible=False,
        showlegend=False,
    ),row=1, col=2
)

fig.add_trace(
    go.Scatter(
        x=df_5_min["t"],
        y=df_5_min['SMA_50'],
        line=dict(color='rgb(95,104,192)', width=1),
        name='SMA_50',
        visible=False,
        showlegend=False,
    ),row=1, col=2
)

fig.add_trace(
    go.Scatter(
        x=df_15_min["t"],
        y=df_15_min['SMA_50'],
        line=dict(color='rgb(95,104,192)', width=1),
        name='SMA_50',
        visible=False,
        showlegend=False,
    ),row=1, col=2
)

fig.add_trace(
    go.Scatter(
        x=df_1_day["t"],
        y=df_1_day['SMA_50'],
        line=dict(color='rgb(95,104,192)', width=1),
        name='SMA_50',
        visible=False,
        showlegend=False,
    ),row=1, col=2
)

fig.add_trace(
    go.Scatter(
        x=df['t'],
        y=df['SMA_200'],
        line=dict(color='rgb(71,77,125)', width=1),
        name='SMA_200',
        showlegend=False
    ),row=1, col=2
)
fig.add_trace(
    go.Scatter(
        x=df_1_min['t'],
        y=df_1_min['SMA_200'],
        line=dict(color='rgb(71,77,125)', width=1),
        name='SMA_200',
        visible=False,
        showlegend=False
    ),row=1, col=2
)
fig.add_trace(
    go.Scatter(
        x=df_5_min['t'],
        y=df_5_min['SMA_200'],
        line=dict(color='rgb(71,77,125)', width=1),
        name='SMA_200',
        visible=False,
        showlegend=False
    ),row=1, col=2
)
fig.add_trace(
    go.Scatter(
        x=df_15_min['t'],
        y=df_15_min['SMA_200'],
        line=dict(color='rgb(71,77,125)', width=1),
        name='SMA_200',
        visible=False,
        showlegend=False
    ),row=1, col=2
)
fig.add_trace(
    go.Scatter(
        x=df_1_day['t'],
        y=df_1_day['SMA_200'],
        line=dict(color='rgb(71,77,125)', width=1),
        name='SMA_200',
        visible=False,
        showlegend=False
    ),row=1, col=2
)




fig.add_trace(go.Scatter(x=df['t'],
                     y=df['v'],
                     # mode="line",
                     showlegend=False,
                     visible=True,
                     xaxis="x3",
                     yaxis="y3",
                     fill='tonexty',
                     fillcolor='rgb(73,76,100)',
                     line = dict(color='rgb(73,76,100)',width=12),
                     ),row=2, col=1)

fig.add_trace(go.Scatter(x=df_1_min['t'],
                     y=df_1_min['v'],
                     # mode="line",
                     showlegend=False,
                     visible=False,
                     xaxis="x12",
                     yaxis="y12",
                     fill='tonexty',
                     fillcolor='rgb(73,76,100)',
                     line = dict(color='rgb(73,76,100)',width=12),
                     ),row=2, col=1)
fig.add_trace(go.Scatter(x=df_5_min['t'],
                     y=df_5_min['v'],
                     # mode="line",
                     showlegend=False,
                     visible=False,
                     xaxis="x13",
                     yaxis="y13",
                     fill='tonexty',
                     fillcolor='rgb(73,76,100)',
                     line = dict(color='rgb(73,76,100)',width=12),
                     ),row=2, col=1)
fig.add_trace(go.Scatter(x=df_15_min['t'],
                     y=df_15_min['v'],
                     # mode="line",
                     showlegend=False,
                     visible=False,
                     xaxis="x14",
                     yaxis="y14",
                     fill='tonexty',
                     fillcolor='rgb(73,76,100)',
                     line = dict(color='rgb(73,76,100)',width=12),
                     ),row=2, col=1)
fig.add_trace(go.Scatter(x=df_1_day['t'],
                     y=df_1_day['v'],
                     # mode="line",
                     showlegend=False,
                     visible=False,
                     xaxis="x15",
                     yaxis="y15",
                     fill='tonexty',
                     fillcolor='rgb(73,76,100)',
                     line = dict(color='rgb(73,76,100)',width=12),
                     ),row=2, col=1)




updatemenus = [{
                'active':0,
                'x':1,
                'y':1.08,
                'buttons': [


                            {'method': 'update',
                             'label': 'Hourly',
                             'args': [
                                      # 1. updates to the traces
                                      {

                                       'visible': [True,False,False,False,False,True,False,False,False,False,True,False,False,False,False,True,False,False,False,False,True,False,False,False,False]},
                                       {
                                        'shapes':get_shapes(df),
                                        'annotations':get_annotations(df),

                                        'xaxis2':{'type':'category','showticklabels':False,
                                        'anchor':'y2',
                                        'rangeslider':{'visible':False},
                                        'domain':[0.23, 1],'showgrid':False,'zeroline':False},
                                        'yaxis2':{
                                        'title':'Price',
                                        'color':'rgb(117,146,194)',
                                        'domain':[0.246,1],
                                        'anchor':'x2',

                                        'ticklen':12,
                                        'ticks':'outside',
                                        'tickcolor':'rgb(35,36,43)','showgrid':False,'zeroline':False,

                                        }
                                        },


                                      ],  },

                            {'method': 'update',
                             'label': '1 Min',
                             'args': [
                                      # 1. updates to the traces
                                      {


                                       'visible': [False,True,False,False,False,False,True,False,False,False,False,True,False,False,False,False,True,False,False,False,False,True,False,False,False]},
                                       {
                                       'shapes':get_shapes(df_1_min),
                                       'annotations':get_annotations(df_1_min),

                                       'xaxis4':{'type':'category','showticklabels':False,
                                       'anchor':'y4',
                                       'rangeslider':{'visible':False},
                                       'domain':[0.23, 1],'showgrid':False,'zeroline':False},
                                       'yaxis4':{
                                       'title':'Price',
                                       'domain':[0.246,1],
                                       'color':'rgb(117,146,194)',
                                       'anchor':'x4',

                                       'ticklen':12,
                                       'ticks':'outside',
                                       'tickcolor':'rgb(35,36,43)','showgrid':False,'zeroline':False,

                                       }
                                       },


                                      ],  },


                            {'method': 'update',
                             'label': '5 Min',
                             'args': [

                                      {

                                       'visible': [False,False,True,False,False,False,False,True,False,False,False,False,True,False,False,False,False,True,False,False,False,False,True,False,False]},
                                       {
                                       'shapes':get_shapes(df_5_min),
                                       'annotations':get_annotations(df_5_min),

                                       'xaxis5':{'type':'category','showticklabels':False,
                                       'anchor':'y5',
                                       'rangeslider':{'visible':False},
                                       'domain':[0.23, 1],'showgrid':False,'zeroline':False},
                                       'yaxis5':{
                                       'title':'Price',
                                       'color':'rgb(117,146,194)',
                                       'domain':[0.246,1],
                                       'anchor':'x5',

                                       'ticklen':12,
                                       'ticks':'outside',
                                       'tickcolor':'rgb(35,36,43)','showgrid':False,'zeroline':False,

                                       }
                                       },

                                      ],  },

                            {'method': 'update',
                             'label': '15 Min',
                             'args': [

                                      {

                                       'visible': [False,False,False,True,False,False,False,False,True,False,False,False,False,True,False,False,False,False,True,False,False,False,False,True,False]},
                                       {
                                       'shapes':get_shapes(df_15_min),
                                       'annotations':get_annotations(df_15_min),

                                       'xaxis6':{'type':'category','showticklabels':False,
                                       'anchor':'y6',
                                       'rangeslider':{'visible':False},
                                       'domain':[0.23, 1],'showgrid':False,'zeroline':False},
                                       'yaxis6':{
                                       'title':'Price',
                                       'color':'rgb(117,146,194)',
                                       'domain':[0.246,1],
                                       'anchor':'x6',

                                       'ticklen':12,
                                       'ticks':'outside',
                                       'tickcolor':'rgb(35,36,43)','showgrid':False,'zeroline':False,

                                       }
                                       },


                                      ],  },



                            {'method': 'update',
                             'label': 'Daily',
                             'args': [

                                       {

                                       'visible': [False,False,False,False,True,False,False,False,False,True,False,False,False,False,True,False,False,False,False,True,False,False,False,False,True]},
                                       {
                                       'shapes':get_shapes(df_1_day),
                                       'annotations':get_annotations(df_1_day),
                                       'xaxis7':{'type':'category','showticklabels':False,
                                       'anchor':'y7',
                                       'rangeslider':{'visible':False},
                                       'domain':[0.23, 1],'showgrid':False,'zeroline':False},
                                       'yaxis7':{
                                       'title':'Price',
                                       'color':'rgb(117,146,194)',
                                       'domain':[0.246,1],
                                       'anchor':'x7',
                                       'ticklen':12,
                                       'ticks':'outside',
                                       'tickcolor':'rgb(35,36,43)','showgrid':False,'zeroline':False,

                                       }
                                       },

                                      ]

                            },],
                'type':'dropdown',
                'direction': 'down',
                'showactive': True,},




    ]



fig.update_layout(
    title = dict(
    text=symbol+" PRICE CHART",
    x=0.5,
    font = dict(size=24)
    ),

    paper_bgcolor='#141d26',
    plot_bgcolor='#141d26',
    font_family='Monospace',
    font_color='rgb(236,242,253)',


    xaxis1 = dict(
            title="Volume",
            domain=[0, 0.2],
            ticklen=12,
            ticks="outside",
            tickcolor='rgb(35,36,43)'
    ),
    yaxis1 = dict(
            title="Volume-Weighted Average Price",
            ticklen=12,
            ticks="outside",
            tickcolor='rgb(35,36,43)',

    ),
    xaxis8 = dict(
            title="Volume",
            domain=[0, 0.2],
            ticklen=12,
            ticks="outside",
            tickcolor='rgb(35,36,43)'
    ),
    yaxis8 = dict(
            title="Volume-Weighted Average Price",
            ticklen=12,
            ticks="outside",
            tickcolor='rgb(35,36,43)',

    ),
    xaxis9 = dict(
            title="Volume",
            domain=[0, 0.2],
            ticklen=12,
            ticks="outside",
            tickcolor='rgb(35,36,43)'
    ),
    yaxis9 = dict(
            title="Volume-Weighted Average Price",
            ticklen=12,
            ticks="outside",
            tickcolor='rgb(35,36,43)',

    ),
    xaxis10 = dict(
            title="Volume",
            domain=[0, 0.2],
            ticklen=12,
            ticks="outside",
            tickcolor='rgb(35,36,43)'
    ),
    yaxis10 = dict(
            title="Volume-Weighted Average Price",
            ticklen=12,
            ticks="outside",
            tickcolor='rgb(35,36,43)',

    ),
    xaxis11 = dict(
            title="Volume",
            domain=[0, 0.2],
            ticklen=12,
            ticks="outside",
            tickcolor='rgb(35,36,43)'
    ),
    yaxis11 = dict(
            title="Volume-Weighted Average Price",
            ticklen=12,
            ticks="outside",
            tickcolor='rgb(35,36,43)',

    ),
    xaxis2=dict(
        rangeslider=dict(
            visible=False
        ),
        showticklabels = False,
        type = "category",
        domain=[0.23, 1]


    ),
    yaxis2 = dict(
        title="Price",
        ticklen=12,
        ticks="outside",
        tickcolor='rgb(35,36,43)'
    ),
    xaxis4=dict(
        rangeslider=dict(
            visible=False
        ),
        showticklabels = False,
        type = "category",
        domain=[0.23, 1]


    ),
    yaxis4 = dict(
        title="Price",
        ticklen=12,
        ticks="outside",
        tickcolor='rgb(35,36,43)'

    ),
    xaxis5=dict(
        rangeslider=dict(
            visible=False
        ),
        showticklabels = False,
        type = "category",
        domain=[0.23, 1]


    ),
    yaxis5 = dict(
        title="Price",
        ticklen=12,
        ticks="outside",
        tickcolor='rgb(35,36,43)'
    ),
    xaxis6=dict(
        rangeslider=dict(
            visible=False
        ),
        showticklabels = False,
        type = "category",
        domain=[0.23, 1]


    ),
    yaxis6 = dict(
        title="Price",
        ticklen=12,
        ticks="outside",
        tickcolor='rgb(35,36,43)'
    ),
    xaxis7=dict(
        rangeslider=dict(
            visible=False
        ),
        showticklabels = False,
        type = "category",
        domain=[0.23, 1]


    ),
    yaxis7 = dict(
        title="Price",
        ticklen=12,
        ticks="outside",
        tickcolor='rgb(35,36,43)'
    ),
    xaxis3 = dict(
    ticks="outside",
    ticklen=12,
    tickcolor="rgb(236,242,253)"
    ),
    yaxis3 = dict(
        title="Volume",
        side="right",
        ticklen=12,
        ticks="outside",
        tickcolor='rgb(35,36,43)'
    ),
    xaxis12 = dict(
    ticks="outside",
    ticklen=12,
    tickcolor="rgb(236,242,253)"
    ),
    yaxis12 = dict(
        title="Volume",
        side="right",
        ticklen=12,
        ticks="outside",
        tickcolor='rgb(35,36,43)'
    ),
    xaxis13 = dict(
    ticks="outside",
    ticklen=12,
    tickcolor="rgb(236,242,253)"
    ),
    yaxis13 = dict(
        title="Volume",
        side="right",
        ticklen=12,
        ticks="outside",
        tickcolor='rgb(35,36,43)'
    ),
    xaxis14 = dict(
    ticks="outside",
    ticklen=12,
    tickcolor="rgb(236,242,253)"
    ),
    yaxis14 = dict(
        title="Volume",
        side="right",
        ticklen=12,
        ticks="outside",
        tickcolor='rgb(35,36,43)'
    ),
    xaxis15 = dict(
    ticks="outside",
    ticklen=12,
    tickcolor="rgb(236,242,253)"
    ),
    yaxis15 = dict(
        title="Volume",
        side="right",
        ticklen=12,
        ticks="outside",
        tickcolor='rgb(35,36,43)'
    ),
    updatemenus=updatemenus,
    shapes=get_shapes(df),
    annotations=get_annotations(df)

)


fig.layout.images = [dict(
        source="https://i.ibb.co/y6PVjyn/logo.png",
        xref="paper", yref="paper",
        x=0.04, y=0.09,
        sizex=0.15, sizey=0.15,
        xanchor="center", yanchor="bottom"
      )
      ]



fig.update_xaxes(showgrid=False, zeroline=False,color="rgb(117,146,194)")
fig.update_yaxes(showgrid=False,zeroline=False,color="rgb(117,146,194)")


fig.write_image(file='fig_candlestick.png',format="png", width=1920, height=1080, scale=2,engine="kaleido")

fig.show()
