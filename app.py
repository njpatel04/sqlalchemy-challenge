import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

#----------------------------------------------------------------------------------------------------------------------
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    date_split = recent_date[0].split('-')

    re_year = int(date_split[0])
    re_month = int(date_split[1])
    re_day = int(date_split[2])

    # Calculate the date 1 year ago from the last data point in the database
    date_year_ago = dt.date(re_year, re_month, re_day) - dt.timedelta(days = 365)
    
    #Query and close the session
    precipitation = session.query(measurement.date, measurement.prcp).\
                            filter(measurement.date >= date_year_ago).all()
    session.close()
    
    # Create list to jasonify with query data  
    all_prcp =[]
    for date, prcp in precipitation:
        temp_dict ={}
        temp_dict["date"] = date
        temp_dict["percipitation"] = prcp
        all_prcp.append(temp_dict)

    return jsonify(all_prcp)

#----------------------------------------------------------------------------------------------------------------------
@app.route("/api/v1.0/stations")
def stationlist():

    #Query station list and close the session
    s_list = session.query(station.station).all()
    session.close()

    #unravel list in to 1D aray
    station_list = list(np.ravel(s_list))

    return jsonify(station_list)

#----------------------------------------------------------------------------------------------------------------------
@app.route("/api/v1.0/tobs")
def tobs():
    recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    date_split = recent_date[0].split('-')

    re_year = int(date_split[0])
    re_month = int(date_split[1])
    re_day = int(date_split[2])

    # Calculate the date 1 year ago from the last data point in the database
    date_year_ago = dt.date(re_year, re_month, re_day) - dt.timedelta(days = 365)
    
    #Query and close the session
    list_station = session.query(measurement.station, func.count(measurement.station)).\
                    group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()

    temp_Observ = session.query(measurement.tobs).\
                filter(measurement.station == list_station[0][0]).\
                filter(measurement.date >= date_year_ago).all()
    
    session.close()

    tobs = list(np.ravel(temp_Observ))

    return jsonify(tobs)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp_calc(start = None, end = None):

    #Calculate sumary for the temp data using fucation
    temp_summary = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]

    #only start date uses this argumate
    if end == None:

        data = session.query(*temp_summary).filter(measurement.date >= start).all()

        temp_data = list(np.ravel(data))
        session.close()
        return jsonify(temp_data)
    
    #start and end will use below summary fucation
    data = session.query(*temp_summary).filter(measurement.date >= start).\
                filter(measurement.date <= end).all()

    temp_data = list(np.ravel(data))
    session.close()
    return jsonify(temp_data)

if __name__ == '__main__':
    app.run(debug=True)
