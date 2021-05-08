var get_routes = async function (nodes, edges, removed) {
    data = {nodes, edges, removed}

    const res = await fetch("/regen", {
        method: 'POST',
        headers: {
            'content-type': 'application/json'
        },
        body: JSON.stringify(data)
    })

    if(!res.ok) {
        console.log("Error: bad request");
    }
    return res.json()
}