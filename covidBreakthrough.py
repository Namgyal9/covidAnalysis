#!/usr/bin/env python
# coding: utf-8

# In[1]:


from dash import Dash, dcc, html, Input, Output
import pandas as pd
import numpy as np
import plotly.express as px


# ### This is just reading the excel file in same directory and it is called df.

# In[2]:



df = pd.read_excel("CovidProtectionEfficacyByCountry.xlsx")
df.dropna(inplace = True)
df


# ### This is reading a csv file from the same directory and it is called df2. The following code just renames columns and filters out some data that won't be used in the visualization. Also the data wasn't how i'd liked it to be according to my version of how story should be told, so I updated the original dataframe values through some basic for loop such that it is easier for me to plot the data according to the standards set by the parameters of plotly graph functions.

# In[3]:


df2 = pd.read_csv("vaccinations-dailyrate.csv")
df2 = df2[["location", "date", "daily_vaccinations"]]
df2.rename(columns = {"location": "COUNTRY"},inplace = True)
df2.dropna(inplace = True)
min_date = df2["date"].min()
max_date = df2["date"].max()
print(min_date)
print(max_date)
country_list = set()
daily_vaccinations = 0


for index, row in df2.iterrows():
    if row["COUNTRY"] not in country_list:
        daily_vaccinations = 0
        country_list.add(row["COUNTRY"])
        daily_vaccinations += row["daily_vaccinations"]
    else:
        daily_vaccinations += row["daily_vaccinations"]
        
    df2.at[index, "daily_vaccinations"] = daily_vaccinations 
    # you can see the full dataframe in file "vaccinations-dailyrate-updated.csv"
df2  


# ### Following is dash and plotly code. The main chunk of what makes the visualizations work. I made 4 interactive graphs.

# In[ ]:


country_names = df['COUNTRY'].unique().tolist()
df_column_names = df[["% People Protected for ORGINAL INFECTION","% People Protected for ORGINAL SEVERE",
                     "% People Protected for OMICRON INFECTION","% People Protected for OMICRON SEVERE"]]
protection_types = df_column_names.columns.tolist()

fig3 = px.scatter(df, x = "% Population vaccinated", y = "% People Protected for OMICRON SEVERE", size = "NUMBER_VACCINES_TYPES_USED",
                  color = "COUNTRY",hover_name = "COUNTRY")
fig4 = px.bar(df, x="WHO_REGION", y="NUMBER_VACCINES_TYPES_USED", color = "% People Protected for OMICRON SEVERE") 


app = Dash(__name__)




app.layout = html.Div([
    html.H1("COVID BREAK THROUGH INFECTION"),
     html.Div([
        html.H2("ChoroplethMap"),
         html.Label("% protected infection"),
         html.Br(),
        dcc.Dropdown(
        id = "choropleth-country-dropdown",
        options=[{'label': protection, 'value': protection} for protection in protection_types],
        value = "% People Protected for OMICRON SEVERE"),
        dcc.Graph(id="choropleth-map"),
        dcc.Markdown('''__ THE MAP SHOWS __ the relation between % People Protected for severe infection" by country.
        It may help explain the reason behind breakthrough infections by showing which countries may be more 
        susceptible due to myriad of reasons such as demographihc or economic or region. In examining the visuals, it can
        be seen that mainly African nations and Russia tend to have less % protected compared its western counterparts''')
    ])
    ,
    html.Div([
        html.H2("Line Plot"),
        html.Label("Countries"),
        html.Br(),
        dcc.Dropdown(
            options=[{'label': country, 'value': country} for country in country_names],
            value = ["Algeria","Congo","Afghanistan","Canada","Argentina"],
            multi=True,id="country-dropdown"
        ),
        dcc.Graph(id="line-chart"),
        dcc.Markdown('''__In this line plot__ it shows the relationship between vaccination and time. Ultimately
        it demonstrates what the vaccination rate is as time progress for each country selected from the 
        drop down. When we compare countries - especially between WHO specific region- it can be seen that for 
        African nations and other small nations -  the vaccination like every country,exponentially or 
        in many cases linearly increases in the beginning stages, but compared to wealthier nations, these nations
        vaccination rate flatlines alot faster and stays that way for remainder of dates available in the dataset''')
    ])
    ,
    html.Div([html.H2("Scatterplot"),
             dcc.Graph(id = "scatterplot",
                      figure = fig3)]),
             dcc.Markdown(''' __As shown by the scatterplot__ as population vaccinated increases, the % protected
             omicron also increases - it is nearly a linear relationship. When hovering over the first half of 
             the graph, you can see that it mainly comprises of known poor countries like Yemen and
             African nations again. Indicating that maybe breakthrough infection is happening due to lack of 
             resources.'''),
    html.Div([
        html.H2("StackedBarChart"),
        dcc.Graph(id="stacked-bar-chart", 
                 figure = fig4),
        dcc.Markdown('''__Last, but not least,___the stacked bar chart tries to infer, building upon the previous
        graph that lack of resources might be the case, that # of vaccines used/available might be factor in %
        people protected for severe. And it is somewhat true. Although there are anomalies especially in EMRO, where
        there are several countries in 20% range, AFRO region is one of the glaring obvious. It has one of 
        the smallest aggregate of % people protected. And also # of vaccines used.
        ''')
    ])
], style={"textAlign": "center"})

@app.callback(
    Output("line-chart", "figure"),
    Input("country-dropdown", "value")
)
def update_figure(selected_countries):
    filtered_df = df2[df2["COUNTRY"].isin(selected_countries)]

    fig = px.line(filtered_df, x="date", y="daily_vaccinations", color="COUNTRY")
    return fig

@app.callback(
    Output("choropleth-map","figure"),
    Input("choropleth-country-dropdown", "value")
)
def update_figure1(protection_type):
    fig1 = px.choropleth(df, locations='COUNTRY', locationmode='country names',
                        color= protection_type,
                        hover_name='COUNTRY',
                        color_continuous_scale=px.colors.sequential.Plasma)
    return fig1




if __name__ == '__main__':
    app.run_server()


# In[ ]:




