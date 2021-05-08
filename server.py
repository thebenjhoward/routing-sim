#!/usr/bin/python3
from utils import graph
from tabulate import tabulate
from flask import Flask, render_template, request, make_response
app = Flask(__name__)

@app.route('/', methods=["GET"])
def index():
    ggraph = graph.gen_graph(10, 2, 6, 6)   
    
    
    ntables, rtables, dtables = [], [], []
    for i in range(len(ggraph.vertices)):
        neighbor_table = graph.neighbor_table(ggraph, i)

        dijkstra, mins = graph.dijkstra_route(ggraph, i)
        dijkstra_table = graph.dijkstra_format(ggraph, dijkstra, mins)
        routing_table = graph.routing_table(ggraph, mins)

        ntables.append(neighbor_table)
        rtables.append(routing_table)
        dtables.append(dijkstra_table)

    js_graph = ggraph.to_json()
    return render_template('index.html.j2', nodes=js_graph['nodes'], edges=js_graph['edges'], 
            dijkstra=dtables, neighbors=ntables, routing=rtables, options={} )

@app.route('/regen', methods=["POST"])
def regen():
    json_data = request.json

    nodes = json_data["nodes"]
    edges = json_data["edges"]
    removed = json_data["removed"]

    nodes[-1]['color'] = {'background': '#d9abff', 'highlight': {'background': '#ead1ff'}}
    nodes[-1]['shape'] = 'box'
    nodes[-2]['color'] = {'background': '#b3f6ff', 'highlight': {'background': '#ccf9ff'}}
    nodes[-2]['shape'] = 'box'

    new_graph = graph.Graph(nodes, edges)

    ntables, rtables, dtables = [], [], []
    for i in [vert['id'] for vert in new_graph.vertices]:

        dijkstra, mins = graph.dijkstra_route(new_graph, i)
        dijkstra_table = graph.dijkstra_format(new_graph, dijkstra, mins)
        routing_table = graph.routing_table(new_graph, mins)
        neighbor_table = graph.neighbor_table(new_graph, i)

        ntables.append(neighbor_table)
        rtables.append(routing_table)
        dtables.append(dijkstra_table)

    for rem_id in removed:
        ntables.insert(rem_id, "Error in retrieving new table")
        rtables.insert(rem_id, "Error in retrieving new table")
        dtables.insert(rem_id, "Error in retrieving new table")
    

    res = make_response({"neighbor_tables": ntables, "routing_tables": rtables, "dtables": dtables})
    res.mimetype = "application/json"

    return res

if __name__ == '__main__':
    app.run(threaded=True, port=5000)
