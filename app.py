
# Importing Toolkit
import pandas as pd    #2.2.2
import numpy as np     #1.26.4
import plotly.express as px  #5.21.0

# Dash Components
import dash   #2.16.1
from dash import Dash, html, dcc, Input, Output,State
import dash_bootstrap_components as dbc   #1.6.0

import joblib  #1.4.0
from joblib import load 
model = load('model_.pkl')


# -------------- Load The Data ------------------ #
df = pd.read_csv("dataa.csv")

# *************************************************************************
# ** Notice: The EDA of This DataSet has Already Done In Kaggle Notebook **
# *************************************************************************

# Clean The Column Names
df.columns = df.columns.str.replace(" ", "_")

df["Job_Title"].replace("Data Engineer 2", "Data Engineer", inplace=True)

# Remove Outliers in Salary
q1, q3 = df["Salary_in_USD"].quantile([0.25, 0.75])
IQR = q3 - q1
lower = q1 - (IQR * 1.5)
upper = q3 + (IQR * 1.5)

filt = (df["Salary_in_USD"] >=lower) & (df["Salary_in_USD"] < upper)
df = df[filt].copy().reset_index(drop=True)

df["Company_Location"].replace("Israel", "Palestine", inplace=True)

# Let's Select Columns That We Work With !!
df = df[["Job_Title", "Employment_Type",  "Experience_Level",  "work_models",
         "Company_Location", "Salary_in_USD", "Company_Size", "Year"]].copy()


# Companues Location
jobs_title = sorted(df["Job_Title"].unique().tolist())
jobs_title.insert(0,"All")

# -------------- Start The App ------------------ #
app = Dash(__name__, external_stylesheets=[dbc.themes.COSMO],suppress_callback_exceptions=True)
# To render on web app
server = app.server

# Sidebar Style
sidebar_style = {
    "position": "fixed",
    "width":"16rem",
    "height":"100vh",
    "top":"0",
    "bottom":"0",
    "left":"0",
    "padding": "20px",
    "background-color": "#ffffff",
}

# Page Contenet Style
content_style = {
    "margin-left":"16rem",
    "margin-right":"0rem",
    "padding": "20px",
    "height": "100%",
    "background-color": "#E1F0FB",
}
# Pages Navigator
pages_dict = {
    "Home" : "/",
    "Locations": "/Locations",
    "Experiences": "/experinces",
    "Salaries Trends": "/TimeSeries",
    "Salary Predication": "/DeployModel",
}



# Modal Alert
def get_alert(job_value, year_value):
    return dbc.Alert(
        [
                html.H2("Warning", style={"font":"bold 30px tahoma"}),
                html.P(
                    f"The Job {job_value} Did Not Exist In {year_value} !!😔😔",
                    style={"font":"bold 22px consolas"}
                ),
                html.Hr(),
                html.P(
                    "Choose Another Job",
                    style={"font":"bold 20px arial"},
                    className="mb-0",
                ),
            ], color="danger",
        style={"box-shadow": "none", "text-shdow":"none"}
    )

# Nav Bar
sidebar = html.Div(
    [
        html.Div([
            html.H2([
                html.Img(
                    src="https://r2.erweima.ai/imgcompressed/compressed_2532a1b290576b140583e05240259d45.webp",
                    style={'height': '60px', 'margin-right': '3px','borderRadius': '40%'}),
                "AI Stats"
            ], style={
                'display': 'flex',
                'align-items': 'center',  # Align items vertically in the flex container
                'font-size': '20px',
                'font-weight': '700',  # Adjust font weight as needed (400 to 700)
                'color': '#0288D1',  # Adjust text color as needed
                'font-family': 'Dancing Script, cursive',  # Specify custom font
            })
        ], 
        className="display-4"),
        dbc.Nav(
            [
                dbc.NavLink(k, href=f"{v}",
                            className="btn", active="exact",
                            style={"margin-bottom": "20px"})
                for k, v in pages_dict.items()
            ],
            vertical=True,
            pills=True,
        ),
        html.Br(),

        # dbc.Label("Year"),
        dcc.Dropdown(
                id="year-menu",
                options=[
                    {
                        "label": html.Span(["All Years"], style={'color': '#1976D2', 'font-size': 17}),
                        "value": "all",
                    },
                    {
                        "label": html.Span([2020], style={'color': '#1976D2', 'font-size': 17}),
                        "value": 2020,
                    },
                    {
                        "label": html.Span([2021], style={'color': '#1976D2', 'font-size': 17}),
                        "value": 2021,
                    },
                    {
                        "label": html.Span([2022], style={'color': '#1976D2', 'font-size': 17}),
                        "value": 2022,
                    },
                    {
                        "label": html.Span([2023], style={'color': '#1976D2', 'font-size': 17}),
                        "value": 2023,
                    },
                    {
                        "label": html.Span([2024], style={'color': '#1976D2', 'font-size': 17}),
                        "value": 2024,
                    },
                ],
                value="all",

                multi=False,
                searchable=False,
                clearable=False,
                style={
                    "color": "#E1F0FB",
                    "border": "0px",
                    "font-family": "tahoma",
                    "margin-bottom": "15px",
                    "background-color": "#E1F0FB"

                }
            ),
        html.Br(),
        dcc.Dropdown(
            id="job-menu",
            options = [
                {"label": html.Span([i], style={'color': '#1976D2', 'font-size': 17}), "value": i,} for i in  jobs_title

            ],
            value="All",
            multi=False,
            optionHeight= 60,
            clearable=False,
            searchable=True,
            style={
                "color":"#E1F0FB",
                "border": "0px",
                "font-family": "tahoma",
                "margin-bottom": "15px",
                "background-color": "#E1F0FB"
            }

        ),


    ],
    style=sidebar_style
)

header=  html.H1(f"", id="header", style={"text-align":"center"})

# page content
content = html.Div(id="page-content", children = [], style = content_style)

# ►►► App Layout
app.layout = html.Div([
    dcc.Location(id = "page-url"),
    sidebar,
    header,
    content,
], className="container-fluid")

# ****************************************************************************
# **************************** Creating Graphs Functions *********************
# ****************************************************************************

# ---------------- Home Page Graphs ----------------
def create_top_job_chart(year):
    if year == "all":
        df_filtered = df.copy()

    else:
        filt = df["Year"] == year  # df[df["Year"] == year]
        df_filtered = df[filt].copy()

    df_filtered = df_filtered["Job_Title"].value_counts().sort_values(ascending=False).head(10)[::-1]

    # Bar Chart of Wanted Job
    fig_wanted_job = px.bar(df_filtered,
                 orientation="h",
                 y = df_filtered.index ,
                 x = (df_filtered / sum(df_filtered)) * 100,
                 # color = df_filtered.index,
                 color_discrete_sequence=["#90CAF9"],
                 title= "Top Demanded Job",
                 labels={"x": "Popularity of Jobs(%)", "Job_Title": "Job Title"},
                 template="plotly",
                 text = df_filtered.apply(lambda x: f"{(x / sum(df_filtered)) * 100:0.2f}%")
                 )

    fig_wanted_job.update_layout(
        showlegend= False,
        title={
            "font": {
                "size": 35,
                "family": "tahoma",
            }
        }
    )

    fig_wanted_job.update_traces(
        textfont = {
                   "family": "consolas",
                   "size": 14,
                    "color":"white"
                   },
        hovertemplate="Job Title: %{label}<br>Popularity (%): %{value}",
    )

    return fig_wanted_job

def create_high_salary_job_chart(year):
    if year == "all":
        df_filtered = df.copy()
    else:
        filt = df["Year"] == year
        df_filtered = df[filt].copy()

    df_filtered = df_filtered.groupby("Job_Title")["Salary_in_USD"].mean().sort_values(ascending=False).head(10)[::-1]

    # Bar Chart of Wanted Job
    fig_wanted_job = px.bar(df_filtered,
                 y = df_filtered.index ,
                 x = df_filtered ,
                 orientation="h",
                 color_discrete_sequence = ["#90CAF9"],
                 title= "Jobs of the Highest Average Salary",
                 labels={"Job_Title": "Job Title", "x": "AVG Salary (USD)"},
                 template="plotly",
                 text_auto = "0.3s"
                 )

    fig_wanted_job.update_layout(
        showlegend= False,
        title={
            "font": {
                "size": 35,
                "family": "tahoma",
            }
        }
    )

    fig_wanted_job.update_traces(
        textfont = {
                   "family": "consolas",
                   "size": 15,
                    "color":"white"
                   },
        hovertemplate="Job Title: %{label}<br>AVG Salary: %{value}",
    )

    return fig_wanted_job

def create_cards(year):
    if year == "all":
        df_filtered = df.copy()
    else:
        filt = df["Year"] == year
        df_filtered = df[filt].copy()

    all_jobs = df_filtered["Job_Title"].nunique()
    avg_salary = df_filtered["Salary_in_USD"].mean()
    avg_salary = f"${avg_salary:0,.0f}"



    return [all_jobs, avg_salary]


# *************** Locations Graphs *************
import plotly.express as px

# *************** Locations Graphs *************
def create_top_locations(year, job):
    chart_title = "Top Location of Jobs"
    
    if year == "all":
        df_filtered = df.copy()
    else:
        filt = df["Year"] == year
        df_filtered = df[filt].copy()

    if job != "All":
        filt = df_filtered["Job_Title"] == job
        df_filtered = df_filtered[filt].copy()

    df_filtered = df_filtered["Company_Location"].value_counts().sort_values(ascending=False).head(5)

    import plotly.express as px

# *************** Locations Graphs *************
import plotly.express as px

def create_top_locations(year, job):
    chart_title = "Top Location of Jobs"
    
    if year == "all":
        df_filtered = df.copy()
    else:
        filt = df["Year"] == year
        df_filtered = df[filt].copy()

    if job != "All":
        filt = df_filtered["Job_Title"] == job
        df_filtered = df_filtered[filt].copy()

    df_filtered = df_filtered["Company_Location"].value_counts().sort_values(ascending=False).head(5)

    if 0 < len(df_filtered) < 3:
        # Create a Map
        fig_wanted_job = px.scatter_geo(df_filtered,
                                        locations=df_filtered.index,
                                        locationmode='country names',
                                        color=df_filtered,
                                        size=df_filtered,
                                        color_continuous_scale=["#FCDDB0", "#FF9F9F", "#EDD2F3"],
                                        color_discrete_sequence=["#FCDDB0", "#FF9F9F", "#EDD2F3"],
                                        template="plotly",
                                        labels={"size": "Popularity",
                                                "location": "Company Location"},
                                        title=chart_title,
                                        opacity=0.8,
                                       )

        fig_wanted_job.update_traces(
            marker=dict(line=dict(color='black', width=1)),
            selector=dict(mode='markers')
        )

        fig_wanted_job.update_layout(geo=dict(showcountries=True),
                                     coloraxis_colorbar=dict(title='Popularity', len=0.4),
                                     coloraxis_showscale=True,
                                     showlegend=True
                                    )

    else:
        # Bar Chart of Wanted Job
        fig_wanted_job = px.bar(df_filtered,
                     # orientation="h",
                     x = df_filtered.index ,
                     y = (df_filtered / sum(df_filtered)) * 100,
                     color_discrete_sequence = ["#90CAF9"],
                     title=chart_title,
                     labels={"y": "Popularity of Jobs(%)", "Company_Location": "Company Location"},
                     template="plotly",
                     text = df_filtered.apply(lambda x: f"{x}\n({(x / sum(df_filtered)) * 100:0.2f}%)")
                     )
        fig_wanted_job.update_traces(
            textfont = {
                       "family": "consolas",
                       "size": 15,
                        "color":"white"
                       },
            hovertemplate="Company Location: %{label}<br>Popularity (%): %{text}",
        )

    fig_wanted_job.update_layout(
        showlegend= False,
        title={
            "font": {
                "size": 35,
                "family": "tahoma",
            }
        },
        hoverlabel={
            "bgcolor": "#C32BAD",
            "font_size": 16,
            "font_family": "tahoma"
        }
    )

    return fig_wanted_job


def create_salary_locations(year, job):
    chart_title = "Top Comapny Location and AVG Salary Per Job"
    df_filtered = ""
    if year == "all":
        df_filtered = df.copy()

    else:
        filt = df["Year"] == year
        df_filtered = df[filt].copy()

    if job == "All":
        df_filtered = df_filtered.copy()

    else:
        filt = df_filtered["Job_Title"] == job
        df_filtered = df_filtered[filt].copy()

    df_filtered = df_filtered.groupby("Company_Location")["Salary_in_USD"].mean().sort_values(ascending=False).head(10)[::-1]

    if len(df_filtered) > 0 and len(df_filtered) < 4:
        fig_salary_job_loc = px.scatter(df_filtered,
                                        x = df_filtered.index,
                                        y = df_filtered,
                                        color=df_filtered.index,
                                        size=df_filtered,
                                        color_discrete_sequence=["#FCDDB0", "#FF9F9F", "#EDD2F3"],
                                        template="plotly",
                                        labels={"y": "AVG Salary(USD)",
                                               "Company_Location": "Company Location"},
                                        title=chart_title ,opacity=0.8

                                        )
        fig_salary_job_loc.update_layout(
            title={
                "font": {
                    "size": 35,
                    "family": "tahoma",
                }
            },
            hoverlabel = {
                "bgcolor":"#222",
                "font_size":14,
                "font_family":"Rockwell"
            }
        )

    else:
        fig_salary_job_loc = px.bar(df_filtered,
                             orientation="h",
                             x = df_filtered,
                             y=df_filtered.index,
                             color_discrete_sequence = ["#90CAF9"],
                             title= chart_title,
                             labels={"x": "AVG Salary(USD)", "Company_Location": "Company Location"},
                             template="plotly",
                             text_auto = "0.3s"
                     )

        fig_salary_job_loc.update_traces(
            textfont = {
                       "family": "consolas",
                       "size": 15,
                        "color":"white"
                       },
            hovertemplate="Company Location: %{label}<br>AVG Salary: %{value}",
        )

    fig_salary_job_loc.update_layout(
        showlegend= False,
        title={
            "font": {
                "size": 35,
                "family": "tahoma",
            }
        },
        hoverlabel={
            "bgcolor": "#C32BAD",
            "font_size": 16,
            "font_family": "tahoma"
        }
    )

    return fig_salary_job_loc


# ================ Experience Graphs ================
def create_bar_experince(year, job):
    chart_title = "Expected Salary Per Experience Level"
    df_filtered = ""
    if year == "all":
        df_filtered = df.copy()

    else:
        filt = df["Year"] == year
        df_filtered = df[filt].copy()

    if job == "All":
        df_filtered = df_filtered.copy()

    else:
        filt = df_filtered["Job_Title"] == job
        df_filtered = df_filtered[filt].copy()

    df_filtered = df_filtered.groupby("Experience_Level")["Salary_in_USD"].mean().sort_values(ascending=False)

    if len(df_filtered) > 0 and len(df_filtered) < 3:
        fig_experience = px.scatter(df_filtered,
                                    x=df_filtered.index,
                                    y=df_filtered,
                                    color=df_filtered.index,
                                    size=df_filtered,
                                    color_discrete_sequence=["#FCDDB0", "#FF9F9F", "#EDD2F3"],
                                    template="plotly",
                                    labels={"y": "AVG Salary",
                                            "Experience_Level": "Experience Level"},
                                    title=chart_title,
                                    opacity=0.8,
                                    )

    else:
        fig_experience = px.bar(df_filtered,
                                x = df_filtered.index,
                                y = df_filtered,
                                color=df_filtered.index,
                               color_discrete_sequence=["#C0DEFF", "#FCDDB0", "#FF9F9F", "#EDD2F3"],
                               template="plotly",
                               title=chart_title,
                                labels={"Experience_Level": "Experience Level", "y":"AVG Salary"},
                                text_auto="0.3s"
                       )

        fig_experience.update_traces(
            textfont = {
                       "family": "consolas",
                       "size": 18,
                        "color":"#111"
                       },
            hovertemplate="Experience Level: %{label}<br>AVG Salary: %{value}",
        )

    fig_experience.update_layout(
        showlegend=False,
        title={
            "font": {
                "size": 28,
                "family": "tahoma",
            }
        },
        hoverlabel={
            "bgcolor": "#90CAF9",
            "font_size": 16,
            "font_family": "tahoma"
        },
        xaxis={
            "tickfont": {
                "family": "arial",
                "size": 15,
            }
        }
    )

    return fig_experience

def create_pie_experince_popularity(year, job):
    df_filtered = ""
    if year == "all":
        df_filtered = df.copy()

    else:
        filt = df["Year"] == year
        df_filtered = df[filt].copy()

    if job == "All":
        df_filtered = df_filtered.copy()

    else:
        filt = df_filtered["Job_Title"] == job
        df_filtered = df_filtered[filt].copy()

    df_filtered = df_filtered["Experience_Level"].value_counts()
    fig_pie_chart = px.pie(values=df_filtered,
                           names=df_filtered.index,
                           hole=0.40, template="plotly",
                           color=df_filtered.index,
                           color_discrete_sequence=["#ADA2FF", "#C0DEFF", "#FCDDB0", "#FF9F9F", "#EDD2F3"],
                           )


    fig_pie_chart.update_traces(
        textinfo="percent+label",
        textposition="outside",
        textfont = {
                   "family": "consolas",
                   "size": 14,
                    "color":"white"
                   },
        hovertemplate="Experience Level: %{label}<br>Frequency: %{value}",
        marker=dict(line=dict(color='#111', width=2))
    )

    fig_pie_chart.update_layout(
        title={
            "font": {
                "size": 28,
                "family": "tahoma",
            }
        },
        hoverlabel={
            "bgcolor": "#90CAF9",
            "font_size": 16,
            "font_family": "tahoma"
        },
    )

    return fig_pie_chart

def create_pie_experties_popularity(year, job):
    df_filtered = ""
    if year == "all":
        df_filtered = df.copy()

    else:
        filt = df["Year"] == year
        df_filtered = df[filt].copy()

    if job == "All":
        df_filtered = df_filtered.copy()

    else:
        filt = df_filtered["Job_Title"] == job
        df_filtered = df_filtered[filt].copy()

    df_filtered = df_filtered["work_models"].value_counts()
    fig_pie_chart = px.pie(values=df_filtered,
                           names=df_filtered.index,
                           hole=0.38, template="plotly",
                           color=df_filtered.index,
                           color_discrete_sequence=["#ADA2FF", "#C0DEFF", "#FCDDB0", "#FF9F9F", "#EDD2F3"],
                           )

    fig_pie_chart.update_traces(
        textinfo="percent+label",
        textposition="outside",
        textfont={
            "family": "consolas",
            "size": 14,
            "color": "white"
        },
        hovertemplate="Work Environment: %{label}<br>Frequency: %{value}",
        marker=dict(line=dict(color='#111', width=2))
    )

    fig_pie_chart.update_layout(
        title={
            "font": {
                "size": 28,
                "family": "tahoma",
            }
        },
        hoverlabel={
            "bgcolor": "#90CAF9",
            "font_size": 16,
            "font_family": "tahoma"
        },
    )

    return fig_pie_chart

# ================== Time Series ===============
def create_year_line_chart(job):
    df_filtered = ""
    if job == "All":
        df_filtered = df.copy()
    else:
        filt = (df["Job_Title"] == job)
        df_filtered = df[filt].copy()

    df_filtered = df_filtered.pivot_table(index="Year", values="Salary_in_USD", aggfunc="mean")

    fig = px.line(df_filtered,
                  x=list(map(lambda x: str(x), df_filtered.index)),
                  y="Salary_in_USD",
                  markers=True,
                  color_discrete_sequence=["#90CAF9"],
                  labels={"x": "Year", "Salary_in_USD": "AVG Salary (USD)"},
                  template="plotly",
                  title=f"{job} Evolution of The Salary",
                  )

    fig.update_traces(marker=dict(size=12,
                                  line=dict(width=2,
                                            color='#9336B4')))


    fig.update_layout(
        title={
            "font": {
                "size": 28,
                "family": "tahoma",
            }
        },
        hoverlabel={
            "bgcolor": "#C32BAD",
            "font_size": 16,
            "font_family": "tahoma"
        }
    )

    return fig

@app.callback(
    Output("year-menu", "style"),
    Output("job-menu", "style"),
    Output("job-menu", "options"),
    Output(component_id="page-content", component_property="children"),

    Input(component_id="page-url", component_property="pathname"),
    Input(component_id="year-menu", component_property="value"),
    Input(component_id="job-menu", component_property="value"),


)
def get_page_content(pathname, year_value, job_value="All"):
    if pathname == "/":
        if year_value == "all":
            jobs_title = sorted(df.loc[:, "Job_Title"].unique().tolist())

        else:
            filt = df["Year"] == year_value

            jobs_title = sorted(df.loc[filt, "Job_Title"].unique().tolist())
            jobs_title.insert(0, "All")


        return [
            # Year Menu
            {
                'display': 'block',
                "color": "#E1F0FB",
                "border": "0px",
                "font-family": "tahoma",
                "margin-bottom": "15px",
                "background-color": "#E1F0FB"
            },

            # Job Menu
            {'display': 'none'},

            [{"label": html.Span([i], style={'color': '#1976D2', 'font-size': 15}), "value": i, }
            for i in jobs_title],

            html.Div([
                dbc.Row([
                    dbc.Col([
                        dbc.Card(
                            dbc.CardBody([
                                html.H3("Availbale Jobs", style={"color":"#ffffff"}),
                                html.H3(create_cards(year_value)[0], id='availbale-job-crd')
                            ], style={"background-color": "#90CAF9", "text-align": "center",
                                      "border": "1px solid #90CAF9", "border-radius": "10px", "margin-bottom": "5px"})
                        ),

                    ]),
                    dbc.Col([
                        dbc.Card(
                            dbc.CardBody([
                                html.H3("Average Salary per year", style={"color":"#ffffff"}),
                                html.H3(create_cards(year_value)[1], id='salary-job-crd')
                            ], style={"background-color": "#90CAF9", "text-align": "center",
                                      "border": "1px solid #90CAF9", "border-radius": "10px",  "margin-bottom": "5px"})
                        ),
                    ]),
                ]),
                html.Br(),

                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id="top-10-job", figure=create_top_job_chart(year_value),
                                  style={"margin-bottom": "10px", "height": "580px"})
                    ], width=12),
                ]),

                html.Hr(),

                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id="high-salary-job", figure=create_high_salary_job_chart(year_value),
                                  style={"margin-bottom": "10px", "height": "580px"})
                    ], width=12),
                ])

            ])
        ]

    elif pathname == "/Locations":
        if year_value == "all":
            jobs_title = sorted(df.loc[:, "Job_Title"].unique().tolist())
            jobs_title.insert(0, "All")
            if job_value not in jobs_title:
                page_content = get_alert(job_value, year_value)
            else:

                page_content = html.Div([

                    html.Br(),
                    dbc.Row([
                        html.H1("Data Science Jobs & Locations",
                                style={"font": "bold 40px tahoma", 'color': '#1976D2',"text-align": "center"})

                    ]),
                    html.Br(),

                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id="top-location", figure=create_top_locations(year_value, job_value),
                                      style={"margin-bottom": "10px", "height": "580px"})
                        ], width=12),
                    ]),

                    html.Hr(),

                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id="top-salary-location", figure=create_salary_locations(year_value, job_value),
                                      style={"margin-bottom": "10px", "height": "580px"})
                        ], width=12),
                    ], style={"border-bottom": "1px solid #90CAF9"})

                ])


        else:
            filt = df["Year"] == year_value

            jobs_title = sorted(df.loc[filt, "Job_Title"].unique().tolist())
            jobs_title.insert(0, "All")
            if job_value not in jobs_title:
                page_content = get_alert(job_value, year_value)
            else:

                page_content = html.Div([

                    html.Br(),
                    dbc.Row([
                        html.H1("Data Science Jobs & Locations", style={"font":"bold 40px tahoma", 'color': '#1976D2',"text-align": "center"})

                    ]),
                    html.Br(),

                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id="top-location", figure=create_top_locations(year_value, job_value),
                                      style={"margin-bottom": "10px", "height": "580px"})
                        ], width=12),
                    ]),

                    html.Hr(),

                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id="top-salary-location", figure=create_salary_locations(year_value, job_value),
                                      style={"margin-bottom": "10px", "height": "580px"})
                        ], width=12),
                    ], style={"border-bottom": "1px solid #90CAF9"})

            ])

        return [
            # Year Menu
            {
                'display': 'block',
                "color": "#E1F0FB",
                "border": "0px",
                "font-family": "tahoma",
                "margin-bottom": "15px",
                "background-color": "#E1F0FB"
            },

            # Job Menu
            {
                'display': 'block',
                "color":"#E1F0FB",
                "border": "0px",
                "font-family": "tahoma",
                "margin-bottom": "15px",
                "background-color": "#E1F0FB"
            },

            [{"label": html.Span([i], style={'color': '#1976D2', 'font-size': 17}), "value": i, }
            for i in jobs_title],

            page_content
        ]


    elif pathname =="/experinces":
        if year_value == "all":
            jobs_title = sorted(df.loc[:, "Job_Title"].unique().tolist())
            jobs_title.insert(0, "All")
            if job_value not in jobs_title:
                page_content = get_alert(job_value, year_value)
            else:

                page_content = html.Div([

                    html.Br(),
                    dbc.Row([
                        html.H1("Data Science Jobs & Experience Level",
                                style={"font": "bold 40px tahoma", 'color': '#1976D2',"text-align": "center"})
                    ]),
                    html.Br(),

                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id="experience-salary", figure=create_bar_experince(year_value, job_value),
                                      style={"margin-bottom": "10px", "height": "600px"})
                        ], width=12),
                    ]),

                    html.Hr(),

                    dbc.Row([
                        dbc.Col([
                            html.H4("Frequency of Demanded Experience", style={"text-align": "center", "margin-top": "10px"}),
                            dcc.Graph(id="large-company", figure=create_pie_experince_popularity(year_value, job_value),
                                      style={"height": "400px"})
                        ], style={"background-color": "rgb(200, 200, 200)", "margin-right":"10px"}),
                        dbc.Col([
                            html.H4("Frequency of Demanded Work Environment", style={"text-align": "center", "margin-top": "10px"}),

                            dcc.Graph(id="medium-company", figure=create_pie_experties_popularity(year_value, job_value),
                                          style={"height": "400px"})
                        ], style={"background-color": "rgb(200, 200, 200)", }),

                    ]),

                ])


        else:
            filt = df["Year"] == year_value

            jobs_title = sorted(df.loc[filt, "Job_Title"].unique().tolist())
            jobs_title.insert(0, "All")
            if job_value not in jobs_title:
                page_content = get_alert(job_value, year_value)
            else:

                page_content = html.Div([

                    html.Br(),
                    dbc.Row([
                        html.H1("Data Science Jobs & Experience Level",
                                style={"font": "bold 40px tahoma", 'color': '#1976D2',"text-align": "center"})
                    ]),
                    html.Br(),

                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id="experience-salary", figure=create_bar_experince(year_value, job_value),
                                      style={"margin-bottom": "10px", "height": "600px"})
                        ], width=12),
                    ]),

                    html.Hr(),

                    dbc.Row([
                        dbc.Col([
                            html.H4("Frequency of Demanded Experience",
                                    style={"text-align": "center", "margin-top": "10px"}),
                            dcc.Graph(id="large-company", figure=create_pie_experince_popularity(year_value, job_value),
                                      style={"height": "400px"})
                        ], style={"background-color": "rgb(200, 200, 200)", "margin-right": "10px"}),
                        dbc.Col([
                            html.H4("Frequency of Demanded Expert Level",
                                    style={"text-align": "center", "margin-top": "10px"}),

                            dcc.Graph(id="medium-company",
                                      figure=create_pie_experties_popularity(year_value, job_value),
                                      style={"height": "400px"})
                        ], style={"background-color": "rgb(200, 200, 200)", }),

                    ]),

                ])

        return [
            # Year Menu
            {
                'display': 'block',
                "color": "#E1F0FB",
                "border": "0px",
                "font-family": "tahoma",
                "margin-bottom": "15px",
                "background-color": "#E1F0FB"
            },

            # Job Menu
            {
                'display': 'block',
                "color": "#E1F0FB",
                "border": "0px",
                "font-family": "tahoma",
                "margin-bottom": "15px",
                "background-color": "#E1F0FB"
            },

            [{"label": html.Span([i], style={'color': '#1976D2', 'font-size': 17}), "value": i, }
             for i in jobs_title],

            page_content
        ]


    elif pathname =="/TimeSeries":
        jobs_title = sorted(df.loc[:, "Job_Title"].unique().tolist())
        jobs_title.insert(0, "All")
        if job_value not in jobs_title:
            page_content = get_alert(job_value, year_value)
        else:
            page_content = html.Div([

                html.Br(),
                dbc.Row([
                    html.H1("Data Science Jobs & Experience Level",
                            style={"font": "bold 40px tahoma", 'color': '#1976D2',"text-align": "center"})
                ]),
                html.Br(),

                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id="year-salary", figure=create_year_line_chart(job_value),
                                  style={"margin-bottom": "10px", "height": "600px"})
                    ], width=12),
                ]),

            ])


        return [
            # Hide Year Menu

            {'display': 'none'},

            {
                'display': 'block',
                "color": "#E1F0FB",
                "border": "0px",
                "font-family": "tahoma",
                "margin-bottom": "15px",
                "background-color": "#E1F0FB"
            },

            [{"label": html.Span([i], style={'color': '#1976D2', 'font-size': 17}), "value": i, }
             for i in jobs_title],

            page_content
        ]

    elif pathname == "/DeployModel":
        # jobs_title within the "/DeployModel" route
        jobs_title = sorted(df.loc[:, "Job_Title"].unique().tolist())
        jobs_title.insert(0, "All")
        salaries=['CLP', 'HUF', 'JPY', 'INR', 'ILS', 'NOK', 'THB', 'PHP', 'USD',
       'MXN', 'ZAR', 'HKD', 'CAD', 'TRY', 'GBP', 'EUR', 'DKK', 'CHF',
       'NZD', 'PLN', 'BRL', 'AUD', 'SGD']
        page_cont = dbc.Row([
        dbc.Col([
            html.H3("Salary Prediction"),
            
            html.Div([
                html.Label([
                    html.Span("Job Title ", className="mr-2"),
                    html.I(className="fas fa-briefcase"),  
                ], className="d-flex align-items-center"), 
                dcc.Dropdown(
                    id="deploy-job-menu",
                    options=[
                        {"label": title, "value": title} for title in jobs_title
                    ],
                    #value="Data Scientist",
                    multi=False,
                    searchable=True,
                    clearable=False,
                    style={"margin-bottom": "15px"}
                ),
            ], style={"margin-bottom": "20px"}),
            
            html.Div([
                html.Label([
                    html.Span("Experience Level ", className="mr-2"),
                    html.I(className="fas fa-user-tie"),  # User tie icon
                ], className="d-flex align-items-center"),
                dcc.Dropdown(
                    id="deploy-experience-menu",
                    options=[
                        {"label": level, "value": level} for level in df["Experience_Level"].unique()
                    ],
                    #value="Mid Level",
                    multi=False,
                    searchable=True,
                    clearable=False,
                    style={"margin-bottom": "15px"}
                ),
            ], style={"margin-bottom": "20px"}),
            
            # Add similar divs for other features
            # Company Size
            html.Div([
                html.Label([
                    html.Span("Company Size ", className="mr-2"),
                    html.I(className="fas fa-building"),  # Building icon
                ], className="d-flex align-items-center"),
                dcc.Dropdown(
                    id="deploy-company-size",
                    options=[
                        {"label": 'Large', "value": 'Large'},
                        {"label": 'small', "value": 'small'},
                        {"label": 'Medium', "value": 'Medium'},  
                    ],
                    #value="Mid Level",
                    multi=False,
                    searchable=True,
                    clearable=False,
                    style={"margin-bottom": "15px"}
                ),
            ], style={"margin-bottom": "20px"}),
            
            # Employment Type 'FT', 'FL', 'CT', 'PT'
            html.Div([
                html.Label([
                    html.Span("Employment Type ", className="mr-2"),
                    html.I(className="fas fa-industry"),  # Industry icon
                ], className="d-flex align-items-center"),
                dcc.Dropdown(
                    id="deploy-industry-menu",
                    options=[{"label": "FT", "value": 'FT'},
                             {"label": "FL", "value": 'FL'},
                             {"label": "CT", "value": 'CT'},
                             {"label": "PT", "value": 'PT'},
                             ],  # Add appropriate options
                    #value='2',
                    multi=False,
                    searchable=True,
                    clearable=False,
                    style={"margin-bottom": "20px"}
                ),
            ], style={"margin-bottom": "20px"}),
            
            # Salary Currency
            html.Div([
                html.Label([
                    html.Span("Salary Currency ", className="mr-2"),
                    html.I(className="fas fa-dollar-sign"),  # Dollar sign icon
                ], className="d-flex align-items-center"),
                dcc.Dropdown(
                    id="deploy-location-menu",
                    options=[
                    {"label": level, "value": level} for level in salaries
                    ],
                    #value="New York",
                    multi=False,
                    searchable=True,
                    clearable=False,
                    style={"margin-bottom": "15px"}
                ),
            ], style={"margin-bottom": "20px"}),
            
            # Remote Ratio
            html.Div([
                html.Label([
                    html.Span("Remote Ratio ", className="mr-2"),
                    html.I(className="fas fa-wifi"),  # Wifi icon
                ], className="d-flex align-items-center"),
                dcc.Input(
                    id="deploy-experience-years",
                    type="number",
                    placeholder="Remote Ratio",
                    style={"margin-bottom": "15px"}
                ),
            ], style={"margin-bottom": "20px"}),
            
            html.Label("Work Year"),
dcc.Dropdown(
    id="deploy-education-menu",
    options=[{"label": "2020", "value": "2020"},
             {"label": "2021", "value": "2021"},
             {"label": "2022", "value": "2022"},
             {"label": "2023", "value": "2023"},
             {"label": "2024", "value": "2024"}],
    #value="Bachelor's Degree",
    multi=False,
    searchable=True,
    clearable=False,
    style={"margin-bottom": "15px"}
),
            
            dbc.Button("Predict Salary", id="deploy-button", color="primary", className="mr-1", n_clicks=0),
            html.Div(id="deploy-output", style={"margin-top": "20px", "color": "red"}),
            html.Div(id="prediction-placeholder")
        ])
])
        
        return [
            {'display': 'none'},  # for 'year-menu.style'
            {'display': 'none'},  # for 'job-menu.style'
            [{"label": job, "value": job} for job in jobs_title],  # for 'job-menu.options'
            page_cont  # for 'page-content.children'
        ]

@app.callback(
    Output("prediction-placeholder", "children"),
    Input("deploy-button", "n_clicks"),
    State("deploy-job-menu", "value"),
    State("deploy-experience-menu", "value"),
    State("deploy-education-menu", "value"),
    State("deploy-company-size", "value"),
    State("deploy-industry-menu", "value"),
    State("deploy-location-menu", "value"),
    State("deploy-experience-years", "value"),
)

def deploy_and_predict_salary(n, job_title, experience_level, experience_years, company_size, employment_type, location, remote_ratio):
    if n is None:
        return ""
    
    print(f"Button Clicked: {n}")
    print(f"Job Title: {job_title}")
    print(f"Experience Level: {experience_level}")
    print(f"Education Level: {experience_years}")
    print(f"Company Size: {company_size}")
    print(f"Industry: {employment_type}")
    print(f"Location: {location}")
    print(f"Experience Years: {remote_ratio}")
  
    
    try:
        # Construct input data as a DataFrame
        input_data = {
            "work_year": [experience_years],
            "experience_level": [experience_level],
            "employment_type": [employment_type],
            "job_title": [job_title],
            "salary_currency": [location],
            "remote_ratio": [remote_ratio],
            "company_size": [company_size]
        }

        input_df = pd.DataFrame(input_data)

        # Load the preprocessor pipeline
        preprocessor = joblib.load('preprocessor_pipeline.pkl')

        # Transform input data using the preprocessor pipeline
        transformed_data = preprocessor.transform(input_df)

        print(f"Input Data: {transformed_data}")

        # Reshape transformed data to 2D array
        transformed_data = transformed_data.reshape(1, -1)

        # Predict salary
        y_pred = model.predict(transformed_data)[0]

        print(f"Predicted Salary: ${y_pred:,.2f}")

        return html.Div(html.Div(f"Predicted Salary: ${y_pred:,.2f}", style={"color": "red"}))

    except Exception as e:
        #print(f"Error predicting salary: {e}")
        #return f"Error predicting salary: {e}"
        pass

if __name__ == "__main__":
    app.run_server(debug=True)
