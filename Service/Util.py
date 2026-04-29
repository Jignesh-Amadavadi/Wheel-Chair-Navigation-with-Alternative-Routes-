import osmnx as ox
from pyproj import Transformer

latlontoxy = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)

def findClosestNode(y, x, G  , transformer = None):
    """
    Find closest node on graph given the map coordinates.

    TODO: If you implemented your own graph (not from OSMNX), add the CRS information to the graph.

    :param y: latitude
    :param x: longitude
    :param G: Graph : networkx graph
    :param transformer: Transformer : pyproj.Transformer
    :return: Int : node id
    """
    if transformer:
        x, y = transformer.transform(x, y)

    return ox.distance.nearest_nodes(G, x, y)

def weight_calculation(slope, length):
    # Apply asymmetric slope penalty: uphill (positive) is penalized more than downhill
    if slope >= 0:
        slope_penalty = slope ** 2
    else:
        slope_penalty = 0.5 * (abs(slope) ** 2)
    weight = length * (1 + slope_penalty)
    return max(weight, 0.1)

 
def updateGraphWeights(G):
    """
    Update the graph weights for each edge to enable wheelchair or foot navigation.

    :param G: Graph : networkx graph
    :return: G with updated edge weights
    """
    # if weight calculated before dont clculate again
    gen = iter(G.edges(data=True))
    data = next(gen)[-1]
    value = data.get('weight',None)

    if value != None:
        return G

    for u, v, k, data in G.edges(keys=True, data=True):
        length = data.get("length", 1)
        slope = data.get("grade", 0)
        highway = data.get("highway", "")
        if highway == 'steps':
            data['weight'] = float('inf')
            data['weight_reverse'] = float('inf')
            continue
        data['weight'] = weight_calculation(slope,length)
        data['weight_reverse'] = weight_calculation(-slope,length)

    return G

    """
    Update the graph weights for each edge to enable wheelchair navigation.

    :param G:  Graph : networkx graph

    TODO: 
        - make sure that steps are not considered during path calculation
        - only if not done in QGIS already:
            - calculate the weight for each edge and add this to the edge data
            - keep in mind
                    - you need to calculate weights for both edge directions
                    - weights can not be negative
    """

def pathsToCoordinates(G, paths, weight):
    """
    :param G: networkx graph
    :param paths: List : List of paths
    :return: List : List of dictionaries [{"path": List of tuples, "length": str}]

    Note: That function is used to convert the paths to coordinates to be used in the frontend.
    Depending on your 'paths' list, you can modify this function to fit your needs.
    But the return format must be same because of frontend.
    """
    returnList = []
    for path in paths:
        totalWeight = sum(G[u][v][0].get(weight, float('inf')) for u, v in zip(path[:-1], path[1:]))
        totalLength = sum(G[u][v][0].get('length', 0) for u, v in zip(path[:-1], path[1:]))

        pathCoordinates = []
        for node in path:
            x,y = latlontoxy.transform(G.nodes[node]['x'], G.nodes[node]['y'])
            pathCoordinates.append((x,y))

        returnList.append({"path": pathCoordinates, "length": f'length: {round(totalLength)} m, weight: {round(totalWeight)}'})
    return returnList
