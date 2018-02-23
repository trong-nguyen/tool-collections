import json
import requests
import dateutil.parser
from os import environ

class Processor(object):
    """
    Wrapper for ShipEngine requests
    """

    URL = 'https://api.shipengine.com/v1'
    END_POINT = '/tracking'
    def __init__(self, key):
        super(Processor, self).__init__()
        self.API_KEY = key

    def track(self, shipment_info):
        url = self.URL + self.END_POINT

        headers = {
            'Content-type': 'application/json',
            'api-key': self.API_KEY,
        }

        params = {
            'carrier_code': shipment_info['carrier'],
            'tracking_number': shipment_info['tracking_number']
        }

        response = requests.get(url, headers=headers, params=params)
        return response.json()

class TrackingStatus(object):
    """
    Output the tracking status to screen
    """
    def __init__(self, verbose):
        self.verbose = verbose

    def to_string(self, status):
        def make_update_string(event):
            if not event:
                return ''

            dt = dateutil.parser.parse(event['occurred_at'])
            dt = '{:<5}'.format(dt.strftime('%m/%d'))
            location = '{}-{}'.format(event.get('state_province', ''), event.get('city_locality', ''))

            return '{} {:20}'.format(dt, location)


        res = []

        if self.verbose:
            headline_fm = '{id} {item}\nStatus: {status}\nDetails: {descriptions}'
            event_fm = '\t{datetime} {location}: {descriptions}'
        else:
            headline_fm = '{latest_update:30} | {status:10} | {item:50}'
            event_fm = '\t{datetime:<5} {location}'

        events = status.get('events', [])
        latest_update = make_update_string(events[0]) if events else 'unknown'

        headline = {
            'item'          : status.get('item', 'Invalid Item Name'),
            'id'            : 'ID ' + status.get('tracking_number', 'invalid_tracking_number'),
            'status'        : status.get('status_description', ''),
            'descriptions'  : status.get(', carrier_status_description', 'no_description'),
            'latest_update' : latest_update
        }

        res.append(headline_fm.format(**headline))

        if self.verbose:
            for event in events:
                dt = dateutil.parser.parse(event['occurred_at'])
                location = '{}-{}'.format(event.get('city_locality', ''), event.get('state_province', ''))
                res.append(event_fm.format(**{
                    'datetime': '{:<5}'.format(dt.strftime('%m/%d')),
                    'location': location,
                    'descriptions': event.get('description', '')
                    }))

        return '\n'.join(res)

def order_by_latest_update(status):
    lowest = 0

    order = {
        'Delivered': 10,
        'Accepted': 9,
        'Unknown': 8,
        'In Transit': 9,
        '': lowest,
    }
    main_stat = status.get('status_description', '')
    update = status.get('events', [])
    latest_update = lowest if not update else dateutil.parser.parse(update[0]['occurred_at'])

    return (latest_update, order[main_stat] if main_stat in order else '')

def track_all(shipments, verbose):
    api_key = environ.get('SHIPENGINE_API_KEY', None)
    if not api_key:
        raise RuntimeError('Please provide api key for ship engine: $export SHIPENGINE_API_KEY=YOUR_KEY')

    processor = Processor(api_key)
    res = map(processor.track, shipments)
    for shipment, r in zip(shipments, res):
        r.update({'item': shipment.get('item', '')})

    res = sorted(res, key=order_by_latest_update, reverse=True)

    status_printer = TrackingStatus(verbose=verbose)
    res = map(status_printer.to_string, res)
    if verbose:
        return ('\n' + '-' * 50 + '\n').join(res)
    else:
        border = '-' * len(res[0])
        res.insert(0, border)
        res.insert(1, '{:30} | {:10} | {:50}'.format('LOCATION', 'STATUS', 'ITEM'))
        res.insert(2, border)
        return '\n'.join(res)

if __name__ == '__main__':
    print '--- TRACKING APP V1.0 ---'
    try:
        shipments = json.loads(open('shipments.json', 'r').read())
    except:
        print 'Cannot load shipments for tracking'
        raise Exception()
    print track_all(shipments, verbose=False)