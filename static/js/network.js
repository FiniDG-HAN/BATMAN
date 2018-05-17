/*!
 * BATMAN Network JavaScript
 * https://github.com/JonathanFeenstra/BATMAN
 *
 * Copyright (c) 2018 Jonathan Feenstra
 * MIT License (https://github.com/JonathanFeenstra/BATMAN/blob/master/LICENSE)
 */

// Select svg element
var svg = d3.select("#network"),
    width = svg.node().getBoundingClientRect().width,
    height = svg.node().getBoundingClientRect().height,
    g = svg.append("g"),
    color = d3.scaleOrdinal(d3.schemeCategory20);
    focus = 0;

// Start D3 Force simulation
var simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(function(d) { return d.id; }))
    .force("charge", d3.forceManyBody()
                       .strength(-150))
    .force("collide", d3.forceCollide(6))
    .force("center", d3.forceCenter(width / 2, height / 2));

// Load JSON data
d3.json("../static/json/network.json", function(error, graph) {
   if (error) throw error;

   // Select links
   var link = g.append("g")
       .attr("class", "link")
       .selectAll("line")
       .data(graph.links)
       .enter().append("line")
       .attr("id", function(d) { return d.source + "-" + d.target; })
       .attr("stroke-width", function(d) { return 1 + (Math.sqrt(d.value)) * 0.7; })
       .style("stroke", function(d) { return "rgba(0,0,0,0.15)"; })
       .on("click", selectLink)
       .on("mouseover", highlightLink)
       .on("mouseleave", unhighlightLink);

   // Select nodes
   var node = g.append("g")
       .selectAll("circle")
       .attr("class", "node")
       .data(graph.nodes)
       .enter().append("g")
       .on("click", selectNode)
       .on("click", toggleFocus)
       .on("mouseover", highlightNode)
       .on("mouseleave", unhighlightNode);

   var nodeIds = graph.nodes.map(function(node) {
     return node["id"];
   });

   // Find directly connecteted nodes and links
   var directConnections = {};

   graph.nodes.forEach(function(d) {
     directConnections[d.id + "," + d.id] = 1;
   });

   graph.links.forEach(function (d) {
     directConnections[d.source + "," + d.target] = 1;
   });

   function neighboring(a, b) {
     return directConnections[a + "," + b] | directConnections[a.id + "," + b.id];
   }

   // Fade/unfade unconnected nodes
   function toggleFocus() {
     if (focus == 0) {
        d = d3.select(this).node().__data__;
        node.transition().style("opacity", function (o) {
          return neighboring(d, o) | neighboring(o, d) ? 1 : 0.1;
        });
        link.transition().style("opacity", function (o) {
          return d.index == o.source.index | d.index == o.target.index ? 1 : 0.1;
        });
        focus = 1;
      } else {
        node.transition().style("opacity", 1);
        link.transition().style("opacity", 1);
        focus = 0;
    }

}

   // Release all nodes
   d3.select("#release").on("click", function() {
      node.each(releaseNode);
      simulation.alpha(0.3).restart();
  });

  // Draw nodes
  node.append("circle")
      .attr("r", 5)
      .attr("fill", function(d) { return color(d.group); })
      .attr("id", function(d) { return d.id; });

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
      .attr("id", function(d) { return d.id + "-label"; })
      .text(function(d) { return d.id; });

  // Add nodes and links to simulation
  simulation
      .nodes(graph.nodes)
      .on("tick", ticked)
      .force("link")
      .links(graph.links);

  // Update on tick
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

  // Fill drop-down menu
  $(document).ready(function() {
    var $dropdown = $("#options");
    $.each(nodeIds, function(key, value) {
      $dropdown.append("<option value=\"" + value + "\">" + value + "</option>");
    });
  });
});

// Handle zoom events
var zoomhandler = d3.zoom()
    .on("zoom", zoomed)
    .scaleExtent([0.1,15]);

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
  selectNode(d);
}

// Get dragsubject
function dragsubject() {
  return simulation.find(d3.event.x, d3.event.y);
}

// Network selection variables
var selectedItem = false;
    selectedFill = false;
    selectedStroke = false;

// Select node
function selectNode(d) {
  if (selectedItem) {
    unselectItem();
  }
  if (selectedItem == document.getElementById(d.id)) {
    focus = 1;
  } else {
    focus = 0;
  }
  selectedItem = document.getElementById(d.id);
  selectedFill = selectedItem.style["fill"];
  selectedStroke = "none";
  selectedItem.style["fill"] = "blue";
  document.getElementById(d.id + "-label").style["fill"] = "blue";
  var info = document.getElementById("info-content");
      releaseButton = document.createElement("input");
      zoomButton = document.createElement("input");
  releaseButton.type = "submit";
  releaseButton.value = "Release node";
  releaseButton.onclick = function() { releaseNode(d); }
  zoomButton.type = "submit";
  zoomButton.value = "Zoom in on node";
  zoomButton.onclick = function() {
    zoomhandler.translateTo(svg, d.x, d.y);
    zoomhandler.scaleTo(svg.transition(), 2);
  }
  info.innerHTML = "<p style=\"color:" + color(d.group) + ";\"><b>"
                 + d.id + " (hitcount)"
                 + "</b></p><p>Type:</p>"
                 + "<p>Also known as:</p>"
                 + "<p>Related articles:</p>"
                 + "<p><a href=\"http://www.uniprot.org/uniprot/?query="
                 + d.id + "&sort=score\">Search UniProt</a></p>";
  info.appendChild(releaseButton);
  info.appendChild(zoomButton);
}

// Select link
function selectLink(d) {
  if (selectedItem) {
    unselectItem();
  }
  var linkId = d.source.id + "-" + d.target.id;
      info = document.getElementById("info-content");
      zoomButton = document.createElement("input");
  selectedItem = document.getElementById(linkId);
  selectedFill = "none";
  selectedStroke = "rgba(0,0,0,0.15)";
  selectedItem.style["stroke"] = "rgba(0,0,255,0.3)";
  zoomButton.type = "submit";
  zoomButton.value = "Zoom in on link";
  zoomButton.onclick = function() {
    zoomhandler.translateTo(svg, (d.source.x + d.target.x) / 2, (d.source.y + d.target.y) / 2);
    zoomhandler.scaleTo(svg.transition(), 2);
  }
  info.innerHTML = "<p><b><span style=\"color:" + color(d.source.group) + ";\">"
                 + d.source.id + "</span> - <span style=\"color:"
                 + color(d.target.group) + ";\">" + d.target.id
                 + "</span></b></p><p>Relationship score:</p>"
                 + "<p>Mutual PubMed articles:</p>";
  info.appendChild(zoomButton);
}

// Unselect item
function unselectItem() {
  selectedItem.style["fill"] = selectedFill;
  selectedItem.style["stroke"] = selectedStroke;
  if (document.getElementById(selectedItem.id + "-label")) {
    document.getElementById(selectedItem.id + "-label").style["fill"] = "black";
  }
}

// Release node
function releaseNode(d) {
  d.fx = d.fy = null;
}

// Network highlighting variables
var highlightedNode = false;
    highlightedLink = false;

// Highlight node
function highlightNode(d) {
  if (highlightedNode) {
    unhighlightNode(highlightedNode);
  }
  highlightedNode = document.getElementById(d.id);
  document.getElementById(d.id + "-label").style["fill"] = "green";
  highlightedNode.style["stroke"] = "rgba(0,255,0,0.8)";
}

// Unhighlight node
function unhighlightNode(d) {
  highlightedNode.style["stroke"] = "none";
  if (highlightedNode != selectedItem) {
    document.getElementById(d.id + "-label").style["fill"] = "black";
  } else {
    document.getElementById(d.id + "-label").style["fill"] = "blue";
  }
}

// Highlight link
function highlightLink(d) {
  if (highlightedLink) {
    unhighlightLink(highlightedLink);
  }
  highlightedLink = document.getElementById(d.source.id + "-" + d.target.id);
  highlightedLink.style["stroke"] = "rgba(0,255,0,0.3)";
}

// Unhighlight link
function unhighlightLink(d) {
  if (highlightedLink != selectedItem) {
    highlightedLink.style["stroke"] = "rgba(0,0,0,0.15)";
  } else {
    highlightedLink.style["stroke"] = "rgba(0,0,255,0.3)";
  }
}

// Zoom event
function zoomed() {
  if (d3.event.sourceEvent && d3.event.sourceEvent.type == "wheel") {
    g.transition().duration(100).attr("transform", d3.event.transform);
  } else {
    g.attr("transform", d3.event.transform);
  }
}

// Expand or collapse advanced options
function toggleAdvanced() {
  var collapsible = document.getElementById("collapsible");
      toggleAdv = document.getElementById("focus-advanced");
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
        filterId = "kwfilter"
                 + (parseInt(div.getElementsByTagName("span").length) + 1);
        label = document.createElement('label');
        span = document.createElement('span');
        keywordFilter = document.createElement('select');
    label.id = filterId;
    span.onclick = function() {
      this.parentNode.outerHTML = "";
    }
    span.innerHTML = "- Remove";
    keywordFilter.innerHTML = document.getElementById("options").innerHTML;
    label.appendChild(span);
    label.appendChild(keywordFilter);
    div.appendChild(label);
}

// Filter the network on keywords
function filterKeywords() {

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
    selectNode(foundNode);
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
