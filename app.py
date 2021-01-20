import datetime as dt
import numpy as np
import pandas as pd
import re
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt
from datetime import timedelta
from dateutil.relativedelta import relativedelta
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Flask Setup
#################################################
app = Flask(__name__)


# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/temp/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    #Convert the query results to a dictionary using date as the key and prcp as the value.
    results = (session.query(Measurement.date, Measurement.tobs).order_by(Measurement.date))

    precipitation_dict = []
    for each_row in results:
        datob_dic = {}
        datob_dic["date"] = each_row.date
        datob_dic["tobs"] = each_row.tobs
        precipitation_dict.append(datob_dic)
    return jsonify(precipitation_dict)



@app.route("/api/v1.0/stations")
def stations():
        # Create session (link) from Python to the DB
    session = Session(engine)

    # Query Stations
    results = session.query(Station.name).all()

    # Convert list of tuples into normal list
    station_details = list(np.ravel(results))

    return jsonify(station_details)

@app.route("/api/v1.0/tobs")
def tob_station():
    # Session form Python to DB
    session = Session(engine)
    # Find last date from the Measurements
    last_d = (session.query(Measurement.date).order_by(Measurement.date.desc()).first())

    lastD_str = str(last_d)
    lastD_str = re.sub("'|,", "",lastD_str)
    latest_date_obj = dt.datetime.strptime(lastD_str, '(%Y-%m-%d)')
    query_start_date = dt.date(latest_date_obj.year, latest_date_obj.month, latest_date_obj.day) - relativedelta(years=1)

    q_station_list = (session.query(Measurement.station, func.count(Measurement.station))
                             .group_by(Measurement.station)
                             .order_by(func.count(Measurement.station).desc())
                             .all())
    
    station_hno = q_station_list[0][0]
    print(station_hno)


    # Return a list of tobs for the year before the final date
    results = (session.query(Measurement.station, Measurement.date, Measurement.tobs)
                      .filter(Measurement.date >= query_start_date)
                      .filter(Measurement.station == station_hno)
                      .all())

    # Create JSON results
    tobs_list = []
    for result in results:
        line = {}
        line["Date"] = result[1]
        line["Station"] = result[0]
        line["Temperature"] = int(result[2])
        tobs_list.append(line)

    return jsonify(tobs_list)











if __name__ == '__main__':
    app.run(debug=True)