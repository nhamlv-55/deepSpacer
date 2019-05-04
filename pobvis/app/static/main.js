

function load_json(path) {
    console.log("loading", path)
    $.ajax({
        url: "/"+path,
        cache: false,
        dataType: "json",
        error: function(jqXHR, textStatus, errorThrown){
            console.log(jqXHR)
            console.log(textStatus)
        },
        success: function(obj) {
            json = obj;
            console.log(json)
            $('#name').text(path.split('/').pop());
            for (i in json.nodes){
                node = json.nodes[i]
                node.value = node.value||node.relative_time;
                node.label = node.label||node.absolute_time;
                node.title = node.title||node.predicate+":"+node.pob_id+" expr:"+node.expr_id+" depth:"+node.depth;
                node.group = node.group||node.predicate;
                node.lemmas = node.lemmas||json.lemmas[node.pob_id]
            }
            var nodes = new vis.DataSet(json.nodes);
            var edges = new vis.DataSet(json.edges);
            var container = document.getElementById('network');
            var options = {
                physics: {
                    enabled: false
                },
                interaction: {
                    dragNodes: false,
                    hover: true,
                    keyboard: {
                        enabled: true,
                        speed: {x: 30, y: 30, zoom: 0.1} 
                    }
                },
                layout: {
                    hierarchical: {
                        direction: 'UD',
                        sortMethod: 'directed',
                    },
                },
                edges:{
                    width: 0.5,
                    selectionWidth: function (width) {return width*2;},
                    arrows: {
                        to:     {enabled: true, type:'arrow'}
                    },
                    smooth: {
                        type: 'cubicBezier',
                        //type: 'diagonalCross',
                        roundness: 0.2
                    },
                    color: {
                        color: 'lightblue',
                        highlight: 'blue'
                    }
                },
                groups: { },
                nodes: {
                    shape: 'dot',
                    scaling: {
                        min: 2,
                        max: 50
                    }
                }
            }
            data = {nodes: nodes, edges: edges};
            network = new vis.Network(container,data,options);
            network.data = data
            console.log(network.data)
            network.on("click", function (params) {
                if(params["nodes"].length){
                    node=network.data.nodes.get(params["nodes"][0]);
                    $('#expr_pob').val(node.expr).show();
                    lemmas = ''
                    for (k in node.lemmas){
                        lemmas+='at depth: '+k;
                        for (j in node.lemmas[k]){
                            lemmas+=", lemma level: " + node.lemmas[k][j].init_level + " to " + node.lemmas[k][j].level+"\n  ";
                            lemmas+=node.lemmas[k][j].expr.replace("\n","\n  ");
                            lemmas+="\n\n";
                        }
                    }
                    $('#expr_lemma').val(lemmas).show();
                }
            });
            network.on("deselectNode", function (params) {
                $('#expr_pob').val('').hide();
                $('#expr_lemma').val('').hide();
                // params["previousSelection"]["nodes"]
            });
        }
    });
} 
