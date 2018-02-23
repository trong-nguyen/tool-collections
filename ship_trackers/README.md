# SHIPMENT TRACKER

An app to track the status of shipments

## Usage

- Configure the input file with a list of your shipment info with mandatory value:
    + tracking_number
    + item: description of your item, not critical
    + carrier: usps/ups/fedex and so on
- Get an API_KEY from http://shipengine.com.
- Export it to the env vars `export SHIPENGINE_API_KEY=YOUR_API_KEY`
- Switch to the app directory `cd PATH_TO_ship_tracker`
- Run the app with `python app.py`