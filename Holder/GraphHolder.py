import networkx as nx
import osmnx as ox
import os
import math
import rasterio  # NEW: for reading DEM CRS

class GraphHolder:
    _graph: nx.DiGraph = None

    def __init__(self):
        pass

    @classmethod
    def get_graph(cls):
        error = FileNotFoundError("Graph is None. Check if the method 'prepareGraph' is implemented.")
        if GraphHolder._graph:
            return GraphHolder._graph
        else:
            if os.path.exists("Data/Bonn.graphml"):
                GraphHolder._graph = ox.load_graphml("Data/Bonn.graphml")
                return GraphHolder._graph
            else:
                GraphHolder._graph = GraphHolder.prepareGraph(
                    cityName='Bonn,Germany',
                    DEMPath="Data/dgm1_05314000_Bonn.tif"
                )
                if GraphHolder._graph is not None:
                    return GraphHolder._graph
                else:
                    raise error

    @classmethod
    def __checkDEMPath(cls, path):
        error = FileNotFoundError(
            "Digital Elevation Model (DEM) does not exist.\n"
            "Is the DEM in the 'Data' folder?\n"
            "You can download it from:\n"
            "https://databox.bonn.de/public/download-shares/nzdFB6N6O3wwB67sGXrBESdVlwF596Ia"
        )
        if os.path.exists(path):
            return path
        else:
            raise error

    @classmethod
    def prepareGraph(cls, cityName, DEMPath):
        """
        Prepares a wheelchair-accessible graph by:
        - downloading OSM data
        - adding elevation and slope from a DEM
        - filtering steep slopes
        - saving the final graph
        """
        try:
            dem_path = cls.__checkDEMPath(DEMPath)
     
            print("[INFO] Downloading road network...")
            G = ox.graph_from_place(cityName, network_type="walk", simplify=False)

            # # Calculate edge lengths using Haversine
            # def haversine_distance(lat1, lon1, lat2, lon2):
            #     R = 6371000  # Earth radius in meters
            #     phi1, phi2 = math.radians(lat1), math.radians(lat2)
            #     d_phi = math.radians(lat2 - lat1)
            #     d_lambda = math.radians(lon2 - lon1)
            #     a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
            #     c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            #     return R * c

            # print("[INFO] Calculating edge lengths (Haversine)...")
            # for u, v, data in G.edges(data=True):
            #     lat1, lon1 = G.nodes[u]["y"], G.nodes[u]["x"]
            #     lat2, lon2 = G.nodes[v]["y"], G.nodes[v]["x"]
            #     data["length"] = haversine_distance(lat1, lon1, lat2, lon2)

            # Do NOT remove steps — handle them in updateGraphWeights()
           
            print("[INFO] Reading raster CRS using rasterio...")
            
            with rasterio.open(dem_path) as dem:
                raster_crs = dem.crs
                print(f"[INFO] Raster CRS: {raster_crs}")

            print("[INFO] Reprojecting graph to raster CRS...")
            G = ox.project_graph(G, to_crs=raster_crs)

            print("[INFO] Adding elevation from DEM...")
            G = ox.add_node_elevations_raster(G, dem_path)

            print("[INFO] Calculating slope (grade)...")
            G = ox.add_edge_grades(G)
            G = ox.project_graph(G, to_crs='4326')

            os.makedirs("Data", exist_ok=True)
            ox.save_graphml(G, "Data/Bonn.graphml")
            print("[SUCCESS] Graph saved to Data/Bonn.graphml")

            return G

        except Exception as e:
            print(f"[ERROR] Graph preparation failed: {e}")
            return None


if __name__ == '__main__':
    GraphHolder.get_graph()
