from OSMPythonTools.api import Api
from OSMPythonTools.overpass import Overpass
from OSMPythonTools.nominatim import Nominatim
from OSMPythonTools.overpass import overpassQueryBuilder, Overpass

nominatim = Nominatim()
areaId = nominatim.query('Shenzhen, China').areaId()

overpass = Overpass()
query = overpassQueryBuilder(area=areaId, elementType='node', selector='"highway"="street_lamp"')
result = overpass.query(query)
print(result)
