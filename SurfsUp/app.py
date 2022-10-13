import numpy as np
import datetime as dt
from datetime import datetime, date, time
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


##################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Print all of the classes mapped to the Base
print(Base.classes.keys())

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

##################################################
#Flask Setup
##################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return """
        Available routes:<br/>
        /api/v1.0/precipitation<br/>
        /api/v1.0/stations<br/>
        /api/v1.0/tobs<br/>
        /api/v1.0/start<br/>
        /api/v1.0/start/end;
    """
#2. Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) 
# to a dictionary using date as the key and prcp as the value.

@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)

    recent_prcp = session.query(str(measurement.date), measurement.prcp)\
    .filter(measurement.date > '2016-08-22')\
    .filter(measurement.date <= '2017-08-23')\
    .order_by(measurement.date).all()

    session.close()

    precip_dict= dict(recent_prcp)

    # return json list of dictionary
    return jsonify(precip_dict)

#3. Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations = session.query(station.name, station.station).all()
    session.close()
    # return json list  
    return jsonify(stations)

#4. Query the dates and temperature observations of the most-active station for the previous year of data.

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    tobs_station = session.query(str(measurement.date), measurement.tobs)\
    .filter(measurement.date > '2016-08-22')\
    .filter(measurement.date <= '2017-08-23')\
    .filter(measurement.station == "USC00519281")\
    .order_by(measurement.date).all()
    session.close()

#Return a JSON list of temperature observations for the previous year.
    return jsonify(tobs_station)

#5. Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.

#For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
#start (string): A date string in the format %Y-%m-%d
# Return a list of TMIN, TMAX, & TAVG for all dates >= to start date.


@app.route("/api/v1.0/<start>")
def start(start):
    """
        start (string): A date string in the format %Y-%m-%d
        Return a list of TMIN, TMAX, & TAVG for all dates >= to start date.
    """
    session = Session(engine)
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    results = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs))\
        .filter(measurement.date >= start_date).all()
    session.close()

    start_tobs = []
    for min, max, avg in results:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Max"] = max
        tobs_dict["Avg"] = avg
        start_tobs.append(tobs_dict)

    return jsonify(start_tobs)

#For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
#start (string): A date string in the format %Y-%m-%d
#end (string): A date string in the format %Y-%m-%d
## Return a list of TMIN, TMAX, & TAVG for all dates between start & end date.

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    """
        start (string): A date string in the format %Y-%m-%d
        end (string): A date string in the format %Y-%m-%d
        Return a list of TMIN, TMAX, & TAVG for all dates between start & end date.
    """
    session = Session(engine)
    start = dt.datetime.strptime(start, '%Y-%m-%d')
    end = dt.datetime.strptime(end, '%Y-%m-%d')
    results = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs))\
        .filter(measurement.date.between(start, end)).all()
    session.close()

    start_to_end_data = []
    for min, max, avg in results:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Max"] = max
        tobs_dict["Avg"] = avg
        start_to_end_data.append(tobs_dict)

    return jsonify(start_to_end_data)

    
if __name__ == '__main__':
    app.run(debug=True)
