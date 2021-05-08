#!/usr/bin/python3
import random
from tabulate import tabulate

def _edges_match(edge1, edge2):
    if((edge1['to'] == edge2['to'] and edge1['from'] == edge2['from']) or
            (edge1['to'] == edge2['from'] and edge1['from'] == edge2['to'])):
        return True
    else:
        return False

class Graph:
    def __init__(self, vertices=None, edges=None):
        if(vertices is None):
            self.vertices = []
        else:
            self.vertices = vertices
        if(edges is None):
            self.edges = []
        else:
            self.edges = edges
        
        self.dijkstra = None
        self.mins = None

    def add_vertex(self, vid, label, **kwargs):
        self.vertices.append({"id":vid, "label":label, **kwargs})

    def add_edge(self, src, dest, cost):
        if(src == dest):
            return

        new_edge = {"from": src, "to": dest, "label": str(cost), "cost": cost}
        
        for edge in self.edges:
            if(_edges_match(edge, new_edge)):
                return

        new_edge['id'] = len(self.edges)
        self.edges.append(new_edge)

    def to_json(self):
        """ Converts the class into a single dictionary with the attributes
            'nodes' and 'edges'
        """
        return { 'nodes' : self.vertices, 'edges' : self.edges }

    def get_neighbors(self, vid):
        if(vid in [vert['id'] for vert in self.vertices]):
            neighbors = []
            for edge in self.edges:
                if(edge['to'] == vid):
                    neighbors.append(edge['from'])
                elif(edge['from'] == vid):
                    neighbors.append(edge['to'])
            return neighbors
        else:
            return []
    
    def get_cost(self, src, dest, do_routing=False):
        if(src == dest):
            return 0
        elif(dest not in self.get_neighbors(src) and do_routing):
            if(self.mins):
                mins = self.mins
            else:
                _, mins = dijkstra_route(self, src)
            cost = [ m for m in mins if m[2] == dest][0][0]
            return cost
        elif(dest not in self.get_neighbors(src)):
            return float('inf')
        else:
            eset = {src, dest}
            for edge in self.edges:
                if({edge['to'], edge['from']} == eset):
                    return edge['cost']
    
    def get_label(self, vid):
        for vertex in self.vertices:
            if(vertex['id'] == vid):
                return vertex['label']

    def get_title(self, vid):
        for vertex in self.vertices:
            if(vertex['id'] == vid):
                return vertex['title']

def gen_graph(n_verts, min_cost, max_cost, max_iface):
    #random.seed(2)
    graph = Graph()
    
    # generate vertices
    for n in range(n_verts):
        if(n == n_verts - 2):
            graph.add_vertex(n, chr(123 - n_verts + n), color={'background': '#b3f6ff', 'highlight': {'background': '#ccf9ff'}}, shape='box', title='192.168.1.{}'.format(255 - n_verts + n))
        elif(n == n_verts - 1):
            graph.add_vertex(n, chr(123 - n_verts + n), color={'background': '#d9abff', 'highlight': {'background': '#ead1ff'}}, shape='box', title='192.168.1.{}'.format(255 - n_verts + n))
        else:
            graph.add_vertex(n, chr(123 - n_verts + n), title='192.168.1.{}'.format(255 - n_verts + n))

    # generate edges
    # it will generate max_iface/2 edges for each vertex
    # edges that connect to itself and edges which are duplicates will not be added
    for n in range(n_verts):
        for _i in range(max_iface // 2):
            graph.add_edge(n, random.randint(0, n_verts - 1), random.randint(min_cost, max_cost))

    return graph

def dijkstra_route(graph, vid):

    graph = Graph(graph.vertices, graph.edges)
    dtable = []
    verts = [ vertex['id'] for vertex in graph.vertices if vertex['id'] != vid]
    mins = []
    min_key = lambda x: x[0]
    
    # step 0
    table_row = []
    for vert in verts:
        table_row.append([graph.get_cost(vid, vert), graph.get_label(vid), vert, vid])
    dtable.append(table_row)
    mins.append(min(table_row, key=min_key))

    # steps 1-X
    k = 1
    curr_vid = mins[0][2]

    while(len(mins) < len(verts)):
        table_row = []
        for i, vert in enumerate(verts):
            if(vert in [x[2] for x in mins]):
                table_row.append([float('inf')])
            else:
                curr_cost = mins[-1][0] + graph.get_cost(curr_vid, vert)
                table_row.append(min(dtable[k-1][i], [curr_cost, graph.get_label(curr_vid), vert, curr_vid], key=min_key))
        dtable.append(table_row)
        mins.append(min(table_row, key=min_key))
        k += 1
        curr_vid = mins[-1][2]

    graph.dijkstra = dtable
    graph.mins = dtable
    return dtable, mins

def dijkstra_format(graph, dtable, mins, html=True):
    dtable.append([[float('inf')]] * len(dtable[0]))

    if(html):
        do_bold = lambda x: "<b>" + x + "</b>"
    else:
        do_bold = lambda x: "\033[1m" + x + "\033[0m"
    
    header_verts = [vert['label'] for vert in graph.vertices if vert['id'] != mins[0][-1]]

    header = ["Step", "N'"]
    header.extend(["D({vert}), p({vert})".format(vert=x) for x in header_verts])

    labels = [mins[0][1]]
    for mval in mins:
        labels.append(labels[-1] + graph.get_label(mval[2]))

    table = []
    for i in range(len(graph.vertices)):
        row = [i, labels[i] ]
        for j, val in enumerate(dtable[i]):
            if(len(val) == 4 and val[0] == float('inf')):
                row.append(u'∞')
            elif(len(val) == 1):
                row.append('-')
            else:
                cellstr = "{}, {}".format(val[0], val[1])
                if(val in mins and dtable[i + 1][j] == [float('inf')]):
                    cellstr = do_bold(cellstr)
                row.append(cellstr)
        table.append(row)
    
    if(html):
        return "<h3>Dijkstra's Algorithm Results</h3>" + tabulate(table, headers=header, tablefmt='unsafehtml')
    else:
        return tabulate(table, headers=header)

def routing_table(graph, mins, html=True):
    root_vert = mins[0][1]
    routes_header = ['Route', 'Interface', 'Total Cost', 'Path*']
    routes = []


    for m in mins:
        if(m[1] == root_vert):
            route = u"{}→{}".format(graph.get_title(m[3]), graph.get_title(m[2]))
            path = u"{}→{}".format(root_vert, graph.get_label(m[2]))
            routes.append([route, graph.get_label(m[2]), m[0], path])
        else:
            curr_m = m
            route = u"{}→{}".format(graph.get_title(mins[0][3]), graph.get_title(m[2]))
            path = u"{}→{}".format(m[1], graph.get_label(m[2]))
            
            while(curr_m[1] != root_vert):
                curr_m = [ mm for mm in mins if curr_m[3] == mm[2]][0]
                path = u"{}→".format(graph.get_label(curr_m[3])) + path
            
            routes.append([route, graph.get_label(curr_m[2]), m[0], path])
    
    if(html):
        return "<h3>Routing Table</h3>" + tabulate(routes, headers=routes_header, tablefmt='html') + "<i>*entire path not necessarily stored by router</i>"
    else:
        return tabulate(routes, headers=routes_header)

def neighbor_table(graph, vid, html=True):
    neighbors = graph.get_neighbors(vid)
    nt_headers = ["Node", "IP/RID", "Cost", "Relationship" ]
    nt_table = []

    if(graph.vertices[-1]['id'] not in neighbors and vid != graph.vertices[-1]['id']):
        neighbors.append(graph.vertices[-1]['id'])
    if(graph.vertices[-2]['id'] not in neighbors and vid != graph.vertices[-2]['id']):
        neighbors.append(graph.vertices[-2]['id'])

    neighbors.sort()

    for nid in neighbors:
        if(nid == graph.vertices[-1]['id'] or nid == graph.vertices[-2]['id']):
            rel = "True Neighbor"
        else:
            rel = "2-Way State Neighbor"
        nt_table.append([graph.get_label(nid), graph.get_title(nid), graph.get_cost(vid, nid, True), rel])
    
    
    if(html):
        return "<h3>OSPF Neighbors</h3>" + tabulate(nt_table, headers=nt_headers, tablefmt="html")
    else:
        return tabulate(nt_table, headers=nt_headers)


if(__name__ == "__main__"):
    ggraph = Graph()
    ggraph.add_vertex(0, 'u')
    ggraph.add_vertex(1, 'v')
    ggraph.add_vertex(2, 'w')
    ggraph.add_vertex(3, 'x')
    ggraph.add_vertex(4, 'y')
    ggraph.add_vertex(5, 'z')
    
    ggraph.add_edge(0, 1, 7)
    ggraph.add_edge(0, 2, 3)
    ggraph.add_edge(0, 3, 5)
    ggraph.add_edge(1, 2, 3)
    ggraph.add_edge(1, 4, 4)
    ggraph.add_edge(2, 3, 4)
    ggraph.add_edge(2, 4, 8)
    ggraph.add_edge(3, 4, 7)
    ggraph.add_edge(3, 5, 9)
    ggraph.add_edge(4, 5, 2)

    dt, minss = dijkstra_route(ggraph, 0)
    
    print(dijkstra_format(ggraph, dt, minss, html=False))
    print(routing_table(ggraph, minss, html=False))

    



