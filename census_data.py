from urllib.request import urlopen
import json

key = 'be1128a4ac78d50e4a840f42bccbff914a19cb7d'
#url_pop_1990 = "https://api.census.gov/data/1990/pep/int_charagegroups?get=POP,RACE_SEX,HISP&&for=county:071&in=state:06&AGEGRP=0&YEAR=90&key=be1128a4ac78d50e4a840f42bccbff914a19cb7d"


def get_fips(latitude, longitude):

	url_loc = urlopen("https://geo.fcc.gov/api/census/block/find?latitude=" + latitude + "&longitude=" + longitude + "&format=json")
	data = json.loads(url_loc.read())
	if data['County'] is None:
		return None
	if data['County']['FIPS'] is None:
		return None

	return (data['County']['FIPS'][:2], data['County']['FIPS'][2:])

def get_population(latitude, longitude, year = "2018"):
	fips = get_fips(latitude, longitude)
	if fips is None:
		return None

	url = urlopen("https://api.census.gov/data/" + year + "/pep/population?get=POP&for=county:" + fips[1] + "&in=state:" + fips[0] + "&key=" + key)
	data = json.loads(url.read())
	return int(data[1][0])

