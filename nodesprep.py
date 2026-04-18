import osmnx as ox

# Define the area (e.g., Central Delhi/Connaught Place)
place_name = "New Delhi, India"

# Download the "drive" network (roads meant for cars)
# You can adjust the 'dist' to get more or fewer nodes
graph = ox.graph_from_place(place_name, network_type='drive')

# Convert to nodes and edges DataFrames
nodes, edges = ox.graph_to_gdfs(graph)

# Now you have 'nodes' (ID, lat, lon) and 'edges' (from_node, to_node, distance)
# You can export these to a JSON or CSV for your "hardcoded" backend
nodes.to_csv("delhi_nodes.csv")
edges.to_csv("delhi_edges.csv")