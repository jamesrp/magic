import json
import urllib2
import time
import datetime
import collections

now = int(time.time()*1000)
start = now
months = 1
end= now + 1000 * 3600 * 31 * months

locations = ["Seattle", "Kirkland", "Bellevue", "Redmond", "Bellingham", "Snohomish", "Everett", "Bellingham"]

# Returns json.
def main_request():
  data = {
    u'count': 30,
    u'filter_mass_markets': True,
    u'request': {
      u'North': 47.88494941538982,
      u'EarliestEventStartDate': None,
      u'LatestEventStartDate': None,
      u'EventTypeCodes': [u'PPTQ'],
      u'West': -122.6002528747731,
      u'ProductLineCodes': [],
      u'SalesBrandCodes': [],
      u'MarketingProgramCodes': [],
      u'PlayFormatCodes': [],
      u'East': -121.9364957252269,
      u'South': 47.437899384610205,
      u'LocalTime': u'/Date(%d)/' % now,
    },
    u'page': 1,
    u'language': u'en-us',
  }

  req = urllib2.Request('http://locator.wizards.com/Service/LocationService.svc/GetLocations')

  req.add_header('Content-Type', 'application/json')

  response = urllib2.urlopen(req, json.dumps(data))
  results = json.loads(response.read())[u'd'][u'Results']
  names = []
  ids = {}
  for i, r in enumerate(results):
    addr = r['Address']
    org = r["Organization"]
    if addr["City"] in locations:
      names.append( '%s: %s' % (addr['City'], addr['Name']) )
      ids[names[-1]] = (org['AddressId'], org['Id'])
  names.sort()
  events = collections.defaultdict(list)
  for n in names:
    for d, t in secondary_request(*ids[n]):
      events[d].append((n, t))
  for d in sorted(events.iterkeys()):
    print d.strftime("%D")
    for n, t in events[d]:
      print "  %s - %s" % (n, t)


def secondary_request(addrID, orgID):
  time.sleep(0.5) # Rate limiting
  data = {
    u'request': {
      u'EarliestEventStartDate': None,
      u'LatestEventStartDate': None,
      u'EventTypeCodes': [u'PPTQ'],
      "BusinessAddressId":addrID,
      "OrganizationId":orgID,
      u'ProductLineCodes': [],
      u'PlayFormatCodes': [],
      u'LocalTime': u'/Date(%d)/' % now,
    },
    u'language': u'en-us',
  }

  req = urllib2.Request('http://locator.wizards.com/Service/LocationService.svc/GetLocationDetails')

  req.add_header('Content-Type', 'application/json')

  response = urllib2.urlopen(req, json.dumps(data))
  results = json.loads(response.read())['d']['Result']
  events = results['EventsAtVenue'] + results['EventsNotAtVenue']
  pptqs = [e for e in events if e['EventTypeCode'] == "PPTQ"]
  for p in pptqs:
    d = datetime.datetime.fromtimestamp(int(p["StartDate"][6:19])/1000)
    yield d, p[u'PlayFormatCode']

main_request()

