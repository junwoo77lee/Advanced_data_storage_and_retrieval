# Dependencies
from flask import Flask, jsonify, render_template
import datetime

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import pandas as pd

# Create an app
app = Flask(__name__)

# Create an engine
engine = create_engine("sqlite:///hawaii.sqlite")


# App routes setting
@app.route("/")
def home():
    # Display available routes as in a table on the home page.
    pd.options.display.max_colwidth = 150 # To display a long string in a cell in the dataframe and 
    df = pd.DataFrame([
                      {'Page' : 'Home', 'Description' : 'The Home page', 'Link' : 'http://127.0.0.1:5000'},
                      {'Page' : 'Precipitation', 'Description' : 'Historical precipitation trend data by date', 'Link' : 'http://127.0.0.1:5000/api/v1.0/precipitation'},
                      {'Page' : 'Stations', 'Description' : 'Weather station information', 'Link' : 'http://127.0.0.1:5000/api/v1.0/stations'},
                      {'Page' : 'Temperature', 'Description' : 'Historical temperature trend data by date', 'Link' : 'http://127.0.0.1:5000/api/v1.0/tobs'},
                      {'Page' : 'Basic stats from start date', 'Description' : 'Basic temperature stats (MIN, AVG, MAX) since the user-input start date', 'Link' : 'Use "Basic stats on temperature" on the right'},
                      {'Page' : 'Basic stats from start date to end date', 'Description' : 'Basic temperature stats (MIN, AVG, MAX) from the user-defined start date to the user-defined end date', 'Link' : 'Use "Basic stats on temperature" on the right'}]             
                      ,columns=['Page', 'Description', 'Link'])
      
    html_data = df.to_html(classes='home', index=False, render_links=True)
    return render_template('index.html', tables=[html_data])


@app.route("/api/v1.0/precipitation")
def get_precipitation_trend():
    # Display precipitations data by date for last 12 months
    query = '''
        SELECT m.date,
               m.prcp
        FROM measurement AS m
        WHERE m.date >= date((SELECT MAX(m2.date) AS last_date FROM measurement AS m2), '-1 year')
    '''

    df = pd.read_sql_query(query, engine)
    df.prcp.dropna(how='any')

    return render_template('precipitation.html', tables=[df.to_html(classes='precipitation', index=False)],
                            title = 'Precipitation data (last 12 months)')

@app.route("/api/v1.0/stations")
def get_stations():
    # Display all the weather station data as in a table
    query = '''
            SELECT *
             FROM station AS s
            '''
    
    df = pd.read_sql_query(query, engine)

    return render_template('base.html', tables=[df.to_html(classes='stations', index=False)],
    title = 'Weather stations')

@app.route("/api/v1.0/tobs")
def get_tobs():
    # Display temperature observations by date for last 12 months
    query = '''
            SELECT m.date,
                   m.tobs
             FROM measurement AS m
             WHERE m.date >= date((SELECT MAX(m2.date) AS last_date
                                   FROM measurement AS m2), '-1 year')
             ORDER BY 1
            '''
    
    df = pd.read_sql_query(query, engine)
    
    return render_template('base.html', tables=[df.to_html(classes='tobs', index=False)],
    title = 'Temperature Observations data (last 12 month)')


@app.route("/api/v1.0/<start>")
def get_basic_stats_start(start):
    # Display basic stats on the temperature data since user-defined start date
    query = f'''
            SELECT MIN(m.tobs) AS Tmin,
                   AVG(m.tobs) AS Tavg,
                   MAX(m.tobs) AS Tmax
             FROM measurement AS m
             WHERE m.date >= '{start}'
            '''
    
    df = pd.read_sql_query(query, engine)
    
    return render_template('base.html', tables=[df.to_html(classes='start')],
    title = 'Basic stats on the temperature observations since user-defined start date')


@app.route("/api/v1.0/<start>/<end>")
def get_basic_stats_strat_end(start, end):
    # Display basic stats on the temperature data between the user-defined start date and end date
    query = f'''
            SELECT MIN(m.tobs) AS Tmin,
                   AVG(m.tobs) AS Tavg,
                   MAX(m.tobs) AS Tmax
             FROM measurement AS m
             WHERE m.date >= '{start}' AND
                   m.date <= '{end}'
            '''
    
    df = pd.read_sql_query(query, engine)
    
    return render_template('base.html', tables=[df.to_html(classes='start_and_end')],
    title = 'Basic stats on the temperature observations based on user-defined start date and end date')



if __name__ == "__main__":
    app.run(debug=True)
