from collections import defaultdict

def convert_edges_to_metis(input_file, output_file, scale=100):
    adjacency = defaultdict(list)
    node_set = set()

    # Step 1: Read and build adjacency list
    with open(input_file, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 3:
                continue  # Skip malformed lines
            u, v, w = parts
            u, v = int(u) + 1, int(v) + 1  # METIS is 1-based
            w = float(w)
            w_scaled = max(1, int(w * scale))  # Ensure weights are positive integers
            adjacency[u].append((v, w_scaled))
            adjacency[v].append((u, w_scaled))  # assuming undirected
            node_set.update([u, v])

    num_nodes = max(node_set)
    num_edges = sum(len(adj) for adj in adjacency.values()) // 2

    # Step 2: Write METIS format
    with open(output_file, 'w') as f:
        f.write(f"{num_nodes} {num_edges} 1\n")  # '1' indicates weighted edges
        for node in range(1, num_nodes + 1):
            neighbors = adjacency.get(node, [])
            line = ' '.join(f"{v} {w}" for v, w in neighbors)
            f.write(line + '\n')

    print(f"Conversion complete. Output saved to: {output_file}")

# Example usage:
if __name__ == "__main__":
    convert_edges_to_metis('bio-CE-GT.edges', 'bio-CE-GT.graph')

