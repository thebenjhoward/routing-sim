// This is the system that will be used for the generation of graphs 


var getRandomInt = (min, max) => {
    min = Math.ceil(min);
    max = Math.floor(max);

    return Math.floor(Math.random() * (max - min) + min);
}

class Vertex {
    constructor(id, label, iface_count) {
        this.id = id; // Unique identifier
        this.label = label; // Name displayed.
        this.iface_count = iface_count; // remaining edges available
    }
}

export default class GraphGenerator {
    constructor(options) {
        this.vertices = [];
        this.edges = [];

        this.options = options;

        this.errors = false;
    }

    get_neighbors(id) {
        let neighbors = [];
        for(let i = 0; i < this.edges.length; i++) {
            if(this.edges[i].from === id) {
                neighbors.push(this.edges[i].to);
            } else if(this.edges[i].to === id) {
                neighbors.push(this.edges[i].from);
            }
        }

        return neighbors;
    }

    make_edge(min_cost, max_cost) {
        let avail_verts = []
        for(let i = 0; i < this.vertices.length; i++) {
            if(this.vertices[i].iface_count > 0) {
                avail_verts.push(i);
            }
        }

        // if only one or zero vertices are left, stop
        console.log(avail_verts);
        if(avail_verts.length <= 1) {
            return false;
        } else if(avail_verts.length === 2) {
            this.edges.push({
                from: avail_verts[0], 
                to: avail_verts[1], 
                label: getRandomInt(min_cost, max_cost)
            });
            return false;
        }

        var to_id = avail_verts[getRandomInt(0, avail_verts.length - 1)];
        var from_id = 0;

        do {
            from_id = avail_verts[getRandomInt(0, avail_verts.length - 1)];
        } while(from_id === to_id)

        let cost = getRandomInt(min_cost, max_cost);

        this.edges.push({from: from_id, to: to_id, label: cost});
        this.vertices[from_id].iface_count -= 1;
        this.vertices[to_id].iface_count -= 1;

        //console.log(this.edges);

        return true;
    }
    
    generate(n_vertices, min_iface, max_iface, min_cost, max_cost) {
        min_iface = Math.max(1, min_iface);
        max_iface = Math.max(min_iface + 1, max_iface);
        
        min_cost = Math.max(1, min_cost);
        max_cost = Math.max(min_cost + 1, max_cost);
        
        console.log({min_iface, max_iface, min_cost, max_cost})
        
        if(!("labelFormat" in this.options)) {
            var label = (n) => "v" + n;
        } else if (this.options.labelFormat === "!a" && n_vertices <= 26) {
            var label = (n) => String.fromCharCode(0x61 + n);
        } else {
            var label = (n) => this.options.labelFormat + n;
        }

        // create vertices
        for(let i = 0; i < n_vertices; i++) {
            this.vertices.push(new Vertex(i, label(i), 
                    getRandomInt(min_iface, max_iface)));
        }

        // generate edges
        while(this.make_edge(min_cost, max_cost)) {}
    }

    get_vis() {
        return {
            nodes: this.vertices,
            edges: this.edges
        };
    }

    get_fresh_vis() {
        this.generate(10, 3, 6, 1, 7);
        console.log("Generated")
        return this.get_vis();
    }
}

