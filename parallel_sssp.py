from mpi4py import MPI
import json
import sys
import math

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Load subgraph for this rank
with open(f"subgraph_part_{rank}.json") as f:
    subgraph = json.load(f)

# Load boundary nodes (used for communication)
with open("boundary_nodes.json") as f:
    boundary_nodes = set(map(int, json.load(f)))

# Convert subgraph keys back to int
graph = {int(k): v for k, v in subgraph.items()}

# Assume source node is 0
source = 0
dist = {int(node): math.inf for node in graph}
if source in dist:
    dist[source] = 0

# Perform Bellman-Ford-like relaxation with MPI sync
for _ in range(100):  # max iterations
    updated = False
    local_updates = {}

    # Relax edges
    for u in graph:
        for v, weight in graph[u]:
            alt = dist[u] + weight
            if v in dist and alt < dist[v]:
                local_updates[v] = alt
                updated = True

    # Sync boundary updates across all ranks
    all_updates = comm.allgather(local_updates)

    for proc_updates in all_updates:
        for node, value in proc_updates.items():
            if node in dist and value < dist[node]:
                dist[node] = value
                updated = True

    flag = comm.allreduce(int(updated), op=MPI.SUM)
    if flag == 0:
        break  # no updates left

# Output results (each rank prints its own distance map)
output_file = f"distances_rank_{rank}.json"
with open(output_file, "w") as f:
    json.dump(dist, f, indent=2)

if rank == 0:
    print("✅ Parallel SSSP complete. Distances saved.")

