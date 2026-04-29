import networkx as nx
from Holder.GraphHolder import GraphHolder
from Service.Util import *
import os

def _shortest_path(lat1, lon1, lat2, lon2, weight="length"):
    graph = GraphHolder.get_graph()
    try:
        source = findClosestNode(lat1, lon1, graph)
        target = findClosestNode(lat2, lon2, graph)
        if source == target:
            raise Exception("Source and target are the same")
        path = nx.dijkstra_path(graph, source, target, weight=weight)
        return pathsToCoordinates(graph, [path], weight)
    except Exception:
        return []

def is_T_local_optimal(path: list, alpha: float, via: int, graph, weight: str) -> bool:
    try:
        via_index = path.index(via)
        forward_distance = sum(graph[u][v][0].get(weight, float('inf')) for u, v in zip(path[:via_index][:-1], path[:via_index][1:]))
        backward_distance = sum(graph[u][v][0].get(weight, float('inf')) for u, v in zip(path[via_index:][:-1], path[via_index:][1:]))
        forward_t = forward_distance * alpha
        backward_t = backward_distance * alpha

        # u_prime: walk backward until ≥ forward_t
        cum_dist = 0
        u_prime = via
        for i in range(via_index - 1, -1, -1):
            u, v = path[i], path[i + 1]
            w = graph[u][v][0].get(weight, 0)
            cum_dist += w
            if cum_dist >= forward_t:
                u_prime = u
                break

        # v_prime: walk forward until ≥ backward_t
        cum_dist = 0
        v_prime = via
        for i in range(via_index, len(path) - 1):
            u, v = path[i], path[i + 1]
            w = graph[u][v][0].get(weight, 0)
            cum_dist += w
            if cum_dist >= backward_t:
                v_prime = v
                break

        sp = nx.shortest_path(graph, u_prime, v_prime, weight=weight)
        return via in sp
    except Exception:
        return False

def _alternative_paths(lat1, lon1, lat2, lon2, weight, via_path_cutoff=0.1, alpha=0.3, gamma=0.5, epsilon=0.25):
    graph = GraphHolder.get_graph()
    try:
        source = findClosestNode(lat1, lon1, graph)
        target = findClosestNode(lat2, lon2, graph)

        opt_path = nx.dijkstra_path(graph, source, target, weight=weight)
        opt_length = sum(graph[u][v][0].get(weight, 0) for u, v in zip(opt_path[:-1], opt_path[1:]))
        max_len = opt_length * (1 + via_path_cutoff)

        source_lengths = nx.single_source_dijkstra_path_length(graph, source, cutoff=max_len, weight=weight)
        target_lengths = nx.single_source_dijkstra_path_length(graph.reverse(copy=False), target, cutoff=max_len, weight=weight)

        via_nodes = {v for v in source_lengths if v in target_lengths and v not in (source, target)}

        alt_paths = []
        accepted_paths = [opt_path]

        def compute_shared_length(p1, p2):
            shared_edges = set(zip(p1[:-1], p1[1:])) & set(zip(p2[:-1], p2[1:]))
            return sum(graph[u][v][0].get(weight, 0) for u, v in shared_edges)

        for via in via_nodes:
            try:
                path1 = nx.dijkstra_path(graph, source, via, weight=weight)
                path2 = nx.dijkstra_path(graph, via, target, weight=weight)
                full_path = path1[:-1] + path2
                full_path = list(dict.fromkeys(full_path))  # remove duplicates

                full_length = sum(graph[u][v][0].get(weight, 0) for u, v in zip(full_path[:-1], full_path[1:]))
                if full_length > opt_length * (1 + epsilon):
                    continue

                shared = compute_shared_length(opt_path, full_path)
                if shared > gamma * opt_length:
                    continue

                if not is_T_local_optimal(full_path, alpha, via, graph, weight):
                    continue

                alt_paths.append(full_path)
                accepted_paths.append(full_path)
                if len(alt_paths) >= 2:
                    break
            except Exception:
                continue

        return pathsToCoordinates(graph, [opt_path] + alt_paths, weight)
    except Exception:
        return []


def shortest_path_by_wheelchair(request):
    try:
        graph = GraphHolder.get_graph()
        updateGraphWeights(graph)
        return _shortest_path(request.lat1, request.lon1, request.lat2, request.lon2, weight="weight")
    except Exception:
        return []


def shortest_path_by_walking(request):
    try:
        return _shortest_path(request.lat1, request.lon1, request.lat2, request.lon2, weight="length")
    except Exception:
        return []


def alternative_paths_by_wheelchair(request, via_path_cutoff=0.1, weight="weight", alpha=None, gamma=None, epsilon=None):
    try:
        graph = GraphHolder.get_graph()
        updateGraphWeights(graph)

        return _alternative_paths(
            request.lat1, request.lon1, request.lat2, request.lon2,
            weight=weight, via_path_cutoff=via_path_cutoff,
            alpha=alpha or request.alpha,
            gamma=gamma or request.gamma,
            epsilon=epsilon or request.epsilon
        )
    except Exception:
        return []

def alternative_paths_by_walking(request, via_path_cutoff=0.1, weight="length", alpha=None, gamma=None, epsilon=None):
    try:
        return _alternative_paths(
            request.lat1, request.lon1, request.lat2, request.lon2,
            weight=weight, via_path_cutoff=via_path_cutoff,
            alpha=alpha or request.alpha,
            gamma=gamma or request.gamma,
            epsilon=epsilon or request.epsilon
        )
    except Exception:
        return []

if __name__ == "__main__":
    os.chdir("../")
