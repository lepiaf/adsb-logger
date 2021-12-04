import json
from datetime import timedelta

from pymongo import MongoClient


def main():
    client = MongoClient('mongodb://adsb:adsb@127.0.0.1')
    db = client['adsb']
    collection = db['aircraft']

    aircraft_collection = collection.find()

    grouped_aircraft = {}
    last_datetime = None
    last_icao = None
    i = 0
    for aircraft in aircraft_collection:

        if aircraft['position'] is None:
            continue

        if aircraft['alt'] > 8000:
            continue

        aircraft['position']['coordinates'].append(round(aircraft['alt']))
        # aircraft['position']['coordinates'].append(datetime.timestamp(aircraft['created_at']))

        if aircraft['icao'] not in grouped_aircraft:
            i = 0
            last_datetime = None
            grouped_aircraft[aircraft['icao']] = {'coordinates': {0: []}, 'datetime': None}

        if last_datetime is None or aircraft['created_at'] <= (last_datetime + timedelta(minutes=5)):
            grouped_aircraft[aircraft['icao']]['coordinates'][i].append(aircraft['position']['coordinates'])
        else:
            i += 1
            grouped_aircraft[aircraft['icao']]['coordinates'][i] = []

        last_datetime = aircraft['created_at']

    geojson = {
        "type": "FeatureCollection",
        "features": []
    }

    for k in grouped_aircraft:
        coordinates = []
        for c in grouped_aircraft[k]['coordinates']:
            coordinates.append(grouped_aircraft[k]['coordinates'][c])
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "MultiLineString",
                "coordinates": coordinates
            },
            "properties": {
                "icao": k,
            }
        }
        geojson['features'].append(feature)

    with open('geo.json', 'w') as f:
        j = json.dumps(geojson)
        f.write(j)
        f.close()


if __name__ == '__main__':
    main()
