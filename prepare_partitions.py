import json
from collections import defaultdict

def read_partition_file(part_file):
    """Reads the METIS partition file"""
    with open(part_file, 'r') as f:
        return [int(line.strip()) for line in f]

def read_graph_file(graph_file):
    """Parses the METIS .graph file into adjacency list"""
    with open(graph_file, 'r') as f:
        header = f.readline()
        num_nodes, num_edges, fmt = map(int, header.strip().split())
        graph = defaultdict(list)
        for idx, line in enumerate(f):
            if not line.strip():
                continue
            entries = list(map(int, line.strip().split()))
            neighbors = [(entries[i] - 1, entries[i + 1]) for i in range(0, len(entries), 2)]
            graph[idx] = neighbors
    return graph

def build_partitioned_subgraphs(graph, partition_map, num_parts):
    """Creates subgraphs based on partition assignments"""
    subgraphs = [defaultdict(list) for _ in range(num_parts)]
    for node, neighbors in graph.items():
        p = partition_map[node]
        for neighbor, weight in neighbors:
            subgraphs[p][node].append((neighbor, weight))
    return subgraphs

def find_boundary_nodes(graph, partition_map):
    """Finds boundary nodes connecting to other partitions"""
    boundary_nodes = set()
    for u in graph:
        pu = partition_map[u]
        for v, _ in graph[u]:
            if partition_map[v] != pu:
                boundary_nodes.add(u)
                break
    return boundary_nodes

def save_subgraphs_to_files(subgraphs):
    """Saves each partition’s subgraph to a JSON file"""
    for i, subgraph in enumerate(subgraphs):
        with open(f"subgraph_part_{i}.json", 'w') as f:
            json.dump({str(k): v for k, v in subgraph.items()}, f, indent=2)

def save_boundary_nodes(boundary_nodes):
    """Saves boundary nodes to a file"""
    with open("boundary_nodes.json", "w") as f:
        json.dump(sorted(list(boundary_nodes)), f, indent=2)

def main():
    graph_file = "bio-CE-GT.graph"
    partition_file = "bio-CE-GT.graph.part.4"
    num_parts = 4

    print("Reading partition file...")
    partition_map = read_partition_file(partition_file)

    print("Reading graph file...")
    graph = read_graph_file(graph_file)

    print("Building subgraphs...")
    subgraphs = build_partitioned_subgraphs(graph, partition_map, num_parts)

    print("Finding boundary nodes...")
    boundary_nodes = find_boundary_nodes(graph, partition_map)

    print("Saving subgraphs...")
    save_subgraphs_to_files(subgraphs)

    print("Saving boundary node info...")
    save_boundary_nodes(boundary_nodes)

    print("✅ All done. Subgraphs and boundary info saved.")

if __name__ == "__main__":
    main()

