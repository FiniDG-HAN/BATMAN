/*!
 * BATMAN Network JavaScript
 * https://github.com/JonathanFeenstra/BATMAN
 *
 * Copyright (c) 2018 Jonathan Feenstra
 * MIT License (https://github.com/JonathanFeenstra/BATMAN/blob/master/LICENSE)
 */

// Select svg
var svg = d3.select("#network"),
    width = svg.node().getBoundingClientRect().width,
    height = svg.node().getBoundingClientRect().height,
    g = svg.append("g"),
    color = d3.scaleOrdinal(d3.schemeCategory20);

// Start simulation
var simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(function(d) { return d.id; }))
    .force("charge", d3.forceManyBody()
                       .strength(-150))
    .force("collide", d3.forceCollide(6))
    .force("center", d3.forceCenter(width / 2, height / 2));

// Get json data
d3.json("../static/json/network.json", function(error, graph) {
   if (error) throw error;

   // Select links
   var link = g.append("g")
       .attr("class", "link")
       .selectAll("line")
       .data(graph.links)
       .enter().append("line")
       .attr("stroke-width", function(d) { return Math.sqrt(d.value); })
       .style("stroke", function(d) { return "rgba(0,0,0,0.15)"; });

   // Select nodes
   var node = g.append("g")
       .selectAll("circle")
       .attr("class", "node")
       .data(graph.nodes)
       .enter().append("g")
       .on('click', releaseNode);

   var nodeIds = graph.nodes.map(function(node) {
     return node["id"];
   });

   // Release all nodes
   d3.select("#release").on("click", function() {
      node.each(releaseNode);
      simulation.alpha(0.3).restart();
  });

  // Draw nodes
  node.append("circle")
      .attr("r", 5)
      .attr("fill", function(d) { return color(d.group); });

  // Handle drag events
  var draghandler = d3.drag()
			.on("start", dragstarted)
			.on("drag", dragged)
			.on("end", dragended);

  draghandler(node);
  zoomhandler(svg);

  // Labels
  node.append("text")
      .attr("dx", 6)
      .text(function(d) { return d.id; });

  // Add nodes and links to simulation
  simulation
      .nodes(graph.nodes)
      .on("tick", ticked)
      .force("link")
      .links(graph.links);

  // On tick
  function ticked() {
    link
        .attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });

    node.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
    }

  // Search autocomplete
  $( function() {
    $("#search").autocomplete({
      source: nodeIds,
      messages: {
        noResults: ""
      },
      autoFocus: true,
      classes: {"ui-autocomplete": "autocomplete"}
    });
  });

  // Fill advanced options
  $(document).ready(function() {
    var $dropdown = $("#options");
    $.each(nodeIds, function(key, value) {
      $dropdown.append("<option value=\"" + value + "\">" + value + "</option>");
    });
  });
});

// Handle zoom events
var zoomhandler = d3.zoom()
    .on("zoom", zoomed);

// Drag events
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
 }

 // Get dragsubject
 function dragsubject() {
   return simulation.find(d3.event.x, d3.event.y);
 }

// Release node
function releaseNode(d) {
  d.fx = d.fy = null;
}

// Zoom event
function zoomed() {
  g.attr("transform", d3.event.transform);
}

// Expand or collapse advanced options
function toggleAdvanced() {
  var collapsible = document.getElementById("collapsible");
      toggleAdv = document.getElementById("toggle-advanced");
  if (collapsible.style["display"] == "block") {
    toggleAdv.innerHTML = "+ More options";
    collapsible.style["display"] = "none";
  } else {
    toggleAdv.innerHTML = "- Hide options";
    collapsible.style["display"] = "block";
  }
}

// Add a keyword filter
function addKeywordFilter() {
    var div = document.getElementById("keyword-filter");
        filterId = "kw-filter"
                 + (parseInt(div.getElementsByTagName("input").length) + 1);
    div.innerHTML += "<label id=\"" + filterId
       + "\"><span onclick=\"javascript:document.getElementById(\'"
       + filterId + "\').outerHTML = \'\'\";>- Remove</span>"
       + "<input type=\"text\" placeholder=\"Bitter gourd, diabetes, etc...\">"
       + "</label>";
}

// Search function
function search() {
  var query = document.getElementById("search").value.toUpperCase();
      node = svg.selectAll("circle");
      foundNode = false;
      otherNodes = node.filter(function(d, i) {
        if (d.id.toUpperCase() == query) {
          foundNode = d;
          }
          return d.id.toUpperCase() != query;
      });
  if (foundNode) {
    document.getElementById("alert").style["display"] = "none";
    otherNodes.style("opacity", "0.1");
    var link = svg.selectAll(".link")
        .style("opacity", "0.1");
    var label = svg.selectAll("text");
    otherLabels = label.filter(function() { return this.innerHTML.toUpperCase() != query;});
    zoomhandler.translateTo(svg, foundNode.x, foundNode.y);
    zoomhandler.scaleTo(svg.transition(), 2);
    otherLabels.style("opacity", "0");
    d3.selectAll("circle, .link, text").transition()
      .duration(2000)
      .style("opacity", 1);
    document.getElementById("info-content").innerHTML = "<p><b>" + foundNode.id
                                           + " (hitcount)"
                                           + "</b></p><p>Also known as:</p>"
                                           + "<p>Related articles:</p>";
  } else {
    document.getElementById("alert").style["display"] = "block";
    document.getElementById("info-content").innerHTML = "<img src=\"../static/img/sadbatman.gif\">";
  }
}

// Set search input with selected value and search
function updateSearch() {
  document.getElementById("search").value = document.getElementById("options").value;
  search();
}
