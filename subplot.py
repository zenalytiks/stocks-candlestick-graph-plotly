import pandas as pd
import pandas_ta as ta
import datetime
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import yfinance as yf

today = str(datetime.datetime.now().date())
svn_days_ago = str((datetime.datetime.now() - datetime.timedelta(days=7)).date())
sixty_days_ago = str((datetime.datetime.now() - datetime.timedelta(days=59)).date())
ten_years_ago = str((datetime.datetime.now() - datetime.timedelta(days=3650)).date())

symbol = 'FB'

df_1_min = yf.download(symbol, start = svn_days_ago, end = today, interval = '1m')

df_5_min = yf.download(symbol, start = sixty_days_ago, end = today, interval = '5m')

df_15_min = yf.download(symbol, start = sixty_days_ago, end = today, interval = '15m')

df = yf.download(symbol, start = sixty_days_ago, end = today, interval = '1h')

df_1_day = yf.download(symbol, start = ten_years_ago, end = today ,interval = '1d')



df_1_min.reset_index(inplace=True)
df_5_min.reset_index(inplace=True)
df_15_min.reset_index(inplace=True)
df.reset_index(inplace=True)
df_1_day.reset_index(inplace=True)

df_1_min.rename(columns={'Datetime':'Date'},inplace=True)
df_5_min.rename(columns={'Datetime':'Date'},inplace=True)
df_15_min.rename(columns={'Datetime':'Date'},inplace=True)
df.rename(columns={'index':'Date'},inplace=True)

df_1_min['Date'] = df_1_min['Date'].astype(str).str.slice(0,19)
df_1_min['Date'] = pd.to_datetime(df_1_min['Date'])
df_5_min['Date'] = df_5_min['Date'].astype(str).str.slice(0,19)
df_5_min['Date'] = pd.to_datetime(df_5_min['Date'])
df_15_min['Date'] = df_15_min['Date'].astype(str).str.slice(0,19)
df_15_min['Date'] = pd.to_datetime(df_15_min['Date'])
df['Date'] = df['Date'].astype(str).str.slice(0,19)
df['Date'] = pd.to_datetime(df['Date'])
df_1_day['Date'] = pd.to_datetime(df_1_day['Date'])


missing_dates = pd.date_range(start = df_1_day['Date'].iloc[0],end=df_1_day['Date'].iloc[-1]).difference(df_1_day.Date).strftime("%Y-%m-%d").tolist()
missing_1_min = pd.date_range(start=df_1_min['Date'].iloc[0],end=df_1_min['Date'].iloc[-1],freq='T').difference(df_1_min.Date).strftime("%Y-%m-%d %H:%M:%S").tolist()
missing_5_min = pd.date_range(start=df_5_min['Date'].iloc[0],end=df_5_min['Date'].iloc[-1],freq='5T').difference(df_5_min.Date).strftime("%Y-%m-%d %H:%M:%S").tolist()
missing_15_min = pd.date_range(start=df_15_min['Date'].iloc[0],end=df_15_min['Date'].iloc[-1],freq='15T').difference(df_15_min.Date).strftime("%Y-%m-%d %H:%M:%S").tolist()
missing_1_hr = pd.date_range(start=df['Date'].iloc[0],end=df['Date'].iloc[-1],freq='1H').difference(df.Date).strftime("%Y-%m-%d %H:%M:%S").tolist()


pd.options.mode.chained_assignment = None



ratios = [0,0.236, 0.382, 0.5 , 0.618, 0.786,1]
def fibonacci_levels(data):
    highest_swing = -1
    lowest_swing = -1
    for i in range(1,data.shape[0]-1):
        if data['High'][i] > data['High'][i-1] and data['High'][i] > data['High'][i+1] and (highest_swing == -1 or data['High'][i] > data['High'][highest_swing]):
            highest_swing = i
        if data['Low'][i] < data['Low'][i-1] and data['Low'][i] < data['Low'][i+1] and (lowest_swing == -1 or data['Low'][i] < data['Low'][lowest_swing]):
            lowest_swing = i

    levels = []
    max_level = data['High'][highest_swing]
    min_level = data['High'][lowest_swing]
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



df.ta.sma(close='Close', length=20, append=True)
df.ta.sma(close='Close', length=50, append=True)
df['vwap'] = (df['Volume']*(df['High']+df['Low'])/2).cumsum() / df['Volume'].cumsum()

df_1_min.ta.sma(close='Close', length=50, append=True)
df_1_min.ta.sma(close='Close', length=200, append=True)
df_1_min['vwap'] = (df_1_min['Volume']*(df_1_min['High']+df_1_min['Low'])/2).cumsum() / df_1_min['Volume'].cumsum()

df_5_min.ta.sma(close='Close', length=50, append=True)
df_5_min.ta.sma(close='Close', length=200, append=True)
df_5_min['vwap'] = (df_5_min['Volume']*(df_5_min['High']+df_5_min['Low'])/2).cumsum() / df_5_min['Volume'].cumsum()

df_15_min.ta.sma(close='Close', length=50, append=True)
df_15_min.ta.sma(close='Close', length=200, append=True)
df_15_min['vwap'] = (df_15_min['Volume']*(df_15_min['High']+df_15_min['Low'])/2).cumsum() / df_15_min['Volume'].cumsum()

df_1_day.ta.sma(close='Close', length=50, append=True)
df_1_day.ta.sma(close='Close', length=200, append=True)
df_1_day['vwap'] = (df_1_day['Volume']*(df_1_day['High']+df_1_day['Low'])/2).cumsum() / df_1_day['Volume'].cumsum()

frames = [df,df_1_min,df_5_min,df_15_min,df_1_day]
labels = ['Hourly','1 Min','5 Min','15 Min','Daily']

fig = make_subplots(
    rows=2, cols=2,
    specs=[[{}, {}],
           [{"colspan": 2}, None]],
    vertical_spacing=0.03,
    row_width=[0.2, 0.7]
    )

for i,frame in zip([1,8,9,10,11],frames):

    if i == 1:
        visibility = True
    else:
        visibility = False
    xaxis = 'x'+str(i)
    yaxis = 'y'+str(i)
    fig.add_trace(
        go.Bar(
            x=frame['Volume'],
            y=frame['vwap'],
            showlegend=False,
            visible=visibility,
            marker_color = "rgb(73,76,100)",
            marker_line_color='rgb(73,76,100)',
            yaxis=yaxis,
            xaxis=xaxis,
            opacity=0.7,
            orientation='h',
            width=1
        ),row=1, col=1
    )


for i,frame in zip([2,4,5,6,7],frames):
    if i == 2:
        visibility = True
    else:
        visibility = False
    xaxis = 'x'+str(i)
    yaxis = 'y'+str(i)
    fig.add_trace(
        go.Candlestick(
            x=frame['Date'],
            open=frame['Open'],
            high=frame['High'],
            low=frame['Low'],
            close=frame['Close'],
            showlegend=False,
            visible=visibility,
            yaxis=yaxis,
            xaxis=xaxis,
            increasing_line_color = "rgb(12,189,113)",
            decreasing_line_color = "rgb(249,74,74)"
        ),row=1, col=2
    )

for i,frame in zip([3,12,13,14,15],frames):
    if i == 3:
        visibility = True
    else:
        visibility = False
    xaxis = 'x'+str(i)
    yaxis = 'y'+str(i)
    fig.add_trace(
        go.Scatter(
            x=frame['Date'],
            y=frame['Volume'],
            # mode="line",
            showlegend=False,
            visible=visibility,
            xaxis=xaxis,
            yaxis=yaxis,
            fill='tonexty',
            fillcolor='rgb(73,76,100)',
            line = dict(color='rgb(73,76,100)',width=12),
        ),row=2, col=1
    )

for i,frame in zip([2,4,5,6,7],frames):
    if i == 2:
        visibility = True
    else:
        visibility = False
    fig.add_trace(
        go.Scatter(
            x=frame['Date'],
            y=frame['SMA_50'],
            line=dict(color='rgb(95,104,192)', width=1),
            name='SMA_50',
            visible=visibility,
            showlegend=False,
        ),row=1, col=2
    )

for i,frame in zip([2,4,5,6,7],frames):
    if i == 2:
        visibility = True
        sma = 'SMA_20'
    else:
        visibility = False
        sma = 'SMA_200'
    fig.add_trace(
        go.Scatter(
            x=frame['Date'],
            y=frame[sma],
            line=dict(color='rgb(71,77,125)', width=1),
            name=sma,
            visible=visibility,
            showlegend=False
        ),row=1, col=2
    )


visible_labels = ['Hourly','1 Min','5 Min','15 Min','Daily','Hourly','1 Min','5 Min','15 Min','Daily','Hourly','1 Min','5 Min','15 Min','Daily','Hourly','1 Min','5 Min','15 Min','Daily','Hourly','1 Min','5 Min','15 Min','Daily']

buttons = []
for i,label,frame in zip([2,4,5,6,7],labels,frames):
    buttons.append(
        {
            'method': 'update',
            'label': label,
            'args': [
                {
                    'visible': [x == label for x in visible_labels]
                },
                {
                    'shapes':get_shapes(frame),
                    'annotations':get_annotations(frame),
                    'xaxis'+str(i):{
                        'type':'category',
                        'showticklabels':False,
                        'anchor':'y'+str(i),
                        'rangeslider':{'visible':False},
                        'domain':[0.23, 1],
                        'showgrid':False,
                        'zeroline':False
                    },
                    'yaxis'+str(i):{
                        'title':'Price',
                        'color':'rgb(117,146,194)',
                        'domain':[0.246,1],
                        'anchor':'x'+str(i),
                        'ticklen':12,
                        'ticks':'outside',
                        'tickcolor':'rgb(35,36,43)',
                        'showgrid':False,
                        'zeroline':False,

                    }
                }


            ]  
        }
    )

updatemenus = [{
    'active':0,
    'x':1,
    'y':1.08,
    'buttons':buttons,
    'type':'dropdown',
    'direction': 'down',
    'showactive': True
}]

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
    updatemenus=updatemenus,
    shapes=get_shapes(df),
    annotations=get_annotations(df)
)


for i in [1,8,9,10,11]:
    fig.update_layout({
        'xaxis'+str(i):{
            'title':'Volume',
            'domain':[0, 0.2],
            'ticklen':12,
            'ticks':"outside",
            'tickcolor':'rgb(35,36,43)'
        },
        'yaxis'+str(i):{
            'title':'Volume-Weighted Average Price',
            'ticklen':12,
            'ticks':'outside',
            'tickcolor':'rgb(35,36,43)'
        }
    }) 

for i in [2,4,5,6,7]:
    fig.update_layout({
        'xaxis'+str(i):{
            'rangeslider':{'visible':False},
            'showticklabels':False,
            'type':'category',
            'domain':[0.23,1]
        },
        'yaxis'+str(i):{
            'title':'Price',
            'ticklen':12,
            'ticks':'outside',
            'tickcolor':'rgb(35,36,43)'
        }
    })

for i,dates,interval in zip([3,12,13,14,15],[missing_1_hr,missing_1_min,missing_5_min,missing_15_min,missing_dates],[3600000,600000,300000,900000,86400000]):
    fig.update_layout({
        'xaxis'+str(i):{
            'ticks':'outside',
            'ticklen':12,
            'tickcolor':'rgb(236,242,253)',
            'rangebreaks':[
                {
                    'values':dates,
                    'dvalue':interval
                }
            ]
        },
        'yaxis'+str(i):{
            'title':'Volume',
            'side':'right',
            'ticklen':12,
            'ticks':'outside',
            'tickcolor':'rgb(35,36,43)'
        }
    })


# fig.layout.images = [dict(
#         source="https://i.ibb.co/y6PVjyn/logo.png",
#         xref="paper", yref="paper",
#         x=0.04, y=0.09,
#         sizex=0.15, sizey=0.15,
#         xanchor="center", yanchor="bottom"
#       )
#       ]



fig.update_xaxes(showgrid=False, zeroline=False,color="rgb(117,146,194)")
fig.update_yaxes(showgrid=False,zeroline=False,color="rgb(117,146,194)")


# fig.write_image(file='fig_candlestick.png',format="png", width=1920, height=1080, scale=2,engine="kaleido")
fig.write_html("candlestick.html")

fig.show()
