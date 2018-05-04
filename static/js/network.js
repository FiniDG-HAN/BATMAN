var svg = d3.select("#network"),
    width = svg.node().getBoundingClientRect().width,
    height = svg.node().getBoundingClientRect().height;

var g = svg.append("g");

var color = d3.scaleOrdinal(d3.schemeCategory20);

var simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(function(d) { return d.id; }))
    .force("charge", d3.forceManyBody())
    .force("collide", d3.forceCollide(6))
    .force("center", d3.forceCenter(width / 2, height / 2));

d3.json("../static/json/network.json", function(error, graph) {
  if (error) throw error;

  var link = g.append("g")
    .attr("class", "link")
    .selectAll("line")
    .data(graph.links)
    .enter().append("line")
    .attr("stroke-width", function(d) { return Math.sqrt(d.value); })
    .style("stroke", function(d) { return "rgba(60,100,200,0.2)"; });

 var node = g.append("g")
    .selectAll("circle")
    .attr("class", "node")
    .data(graph.nodes)
    .enter().append("g")
    .on('click', releaseNode);

  d3.select("#release").on("click", function() {
    node.each(releaseNode);
    simulation.restart();
  });

  node.append("circle")
      .attr("r", 5)
      .attr("fill", function(d) { return color(d.group); });

  var draghandler = d3.drag()
			.on("start", dragstarted)
			.on("drag", dragged)
			.on("end", dragended);

  draghandler(node);

  var zoomhandler = d3.zoom()
      .on("zoom", zoomed);

  zoomhandler(svg);

  // Labels
  node.append("text")
      .attr("dx", 6)
      .text(function(d) { return d.id; });

  simulation
      .nodes(graph.nodes)
      .on("tick", ticked);

  simulation.force("link")
      .links(graph.links);

  function ticked() {
    link
        .attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });

    node.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
    }

  function dragsubject() {
    return simulation.find(d3.event.x, d3.event.y);
  }

  // Autocomplete
  $( function() {
    var nodeIds = graph.nodes.map(function(node) {
      return node["id"];
    });
    $( "#search" ).autocomplete({
      source: nodeIds,
      autoFocus: true,
      classes: {"ui-autocomplete": "autocomplete"}
    });
  } );

});

function dragstarted(d) {
   if (!d3.event.active) simulation.alphaTarget(0.3).restart();
   d.fx = d.x;
   d.fy = d.y;
 }

 function dragged(d) {
   d.fx = d3.event.x;
   d.fy = d3.event.y;
 }

 function dragended(d) {
  if (!d3.event.active) simulation.alphaTarget(0);
   //d.fx = null;
   //d.fy = null;
 }

function releaseNode(d) {
  d.fx = d.fy = null;
}

function zoomed() {
  g.attr("transform", d3.event.transform);
}

function search() {
  var query = document.getElementById('search').value;
  var node = svg.selectAll("circle");
  if (query == "none") {
    console.log("none");
  } else {
    var otherNodes = node.filter(function(d, i) {
        return d.id != query;
    });
    otherNodes.style("opacity", "0");
    var link = svg.selectAll(".link");
    link.style("opacity", "0");
    var label = svg.selectAll("text");
        otherLabels = label.filter(function(){
          return this.innerHTML != query;
        });
    otherLabels.style("opacity", "0");
    d3.selectAll("circle, .link, text").transition()
      .duration(3000)
      .style("opacity", 1);
  }
}
