/*!
 * BATMAN Network JavaScript
 * https://github.com/JonathanFeenstra/BATMAN
 *
 * Copyright (c) 2018 Jonathan Feenstra
 * MIT License (https://github.com/JonathanFeenstra/BATMAN/blob/master/LICENSE)
 *
 * This script is responsible for the network visualisation and the related
 * functionality, including searching and filtering.
 *
 * Known bugs: none. 
 */

// Select svg element
var svg = d3.select("#network"),
        width = svg.node().getBoundingClientRect().width,
        height = svg.node().getBoundingClientRect().height,
        g = svg.append("g"),
        color = d3.scaleOrdinal(d3.schemeCategory20);
focus = false;

// Start D3 Force simulation
var simulation = d3.forceSimulation()
        .force("link", d3.forceLink().id(function (d) {
            return d.id;
        }))
        .force("charge", d3.forceManyBody()
                .strength(-150))
        .force("collide", d3.forceCollide(function (d) {
            return 4 + (d.hitcount / 500000) * 4;
        }))
        .force("center", d3.forceCenter(width / 2, height / 2));

// Load JSON data
d3.json("../static/json/network.json", function (error, graph) {
    if (error)
        throw error;

    // Select links
    var link = g.append("g")
            .attr("class", "link")
            .selectAll("line")
            .data(graph.links)
            .enter().append("line")
            .attr("id", function (d) {
                return d.source + "-" + d.target;
            })
            .attr("stroke-width", function (d) {
                return 1.4 + (Math.sqrt(d.value));
            })
            .style("stroke", function (d) {
                return "rgba(0,0,0,0.12)";
            })
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
            .on("dblclick", toggleFocus)
            .on("mouseover", highlightNode)
            .on("mouseleave", unhighlightNode);

    // Draw nodes
    node.append("circle")
            .attr("r", function (d) {
                return 4 + (d.hitcount / 500000) * 4;
            })
            .attr("fill", function (d) {
                return color(d.group);
            })
            .attr("id", function (d) {
                return d.id;
            });

    // Labels
    node.append("text")
            .attr("dx", 6)
            .attr("id", function (d) {
                return d.id + "-label";
            })
            .text(function (d) {
                return d.id;
            });

    var nodeIds = graph.nodes.map(function (node) {
        return node["id"];
    });

    // Find directly connected nodes and links
    var directConnections = {};

    graph.links.forEach(function (d) {
        directConnections[d.source + "," + d.target] = 1;
    });

    function neighboring(a, b) {
        return directConnections[a + "," + b] || directConnections[a.id + "," + b.id] || a.id === b.id;
    }

    // Fade/unfade unconnected nodes when selecting a node
    function toggleFocus(d) {
        if (d3.event) {
            d3.event.stopPropagation();
        }
        if (!focus) {
            node.style("opacity", function (o) {
                return neighboring(d, o) | neighboring(o, d) ? 1 : 0.1;
            });
            link.style("opacity", function (o) {
                return d.index === o.source.index | d.index === o.target.index ? 1 : 0.1;
            });
            focus = true;
        } else {
            node.style("opacity", 1);
            link.style("opacity", 1);
            focus = false;
        }
    }


    // Download CSV file for a node or link
    function generateCSV(d) {
      if (typeof(d.articles)=='undefined')
        window.alert("No articles for this node or link available");
      var array = d.articles;

        var str = 'PubMedID,ArticleTitle,ArticleAuthors,Date' + '\r\n';

        for (var i = 0; i < array.length; i++) {
            var line = '';

            for (var index in array[i]) {
                line += array[i][index] + ',';
            }

            line.slice(0,line.Length-1);

            str += line + '\r\n';
        }
        window.open( "data:text/csv;charset=utf-8," + escape(str))
    }

    // Remove node
    function removeNode(d) {
        if (selectedItem) {
            unselectItem();
            document.getElementById("info-content").innerHTML = "<p>Node <span style=\"color:"
                    + color(d.group) + ";\">" + d.id + "</span> removed.</p>";
        }
        if (highlightedNode) {
            unhighlightNode(highlightedNode);
            highlightedNode = false;
        }
        if (focus) {
            toggleFocus(d);
        }
        nodeIds = nodeIds.filter(function (id) {
            return d.id !== id;
        });
        $("#search").autocomplete({source: nodeIds});
        document.getElementById(d.id + "-option").outerHTML = "";
        graph.nodes.splice(d.index, 1);
        graph.links = graph.links.filter(function (l) {
            return l.source.id !== d.id && l.target.id !== d.id;
        });
        directConnections = {};
        graph.links.forEach(function (d) {
            directConnections[d.source.id + "," + d.target.id] = 1;
        });
        if (d3.event) {
            d3.event.stopPropagation();
        }
        node = node.data(graph.nodes, function (d) {
            return d.id;
        });
        node.exit().remove();
        node = node.enter().append("circle").attr("fill", function (d) {
            return color(d.group);
        })
                .attr("r", function (d) {
                    return 4 + (d.hitcount / 500000) * 4;
                })
                .merge(node);
        node.select("text").remove();
        node.append("text")
                .attr("dx", 6)
                .attr("id", function (d) {
                    return d.id + "-label";
                })
                .text(function (d) {
                    return d.id;
                });
        link = link.data(graph.links, function (d) {
            return d.source.id + "-" + d.target.id;
        });
        link.exit().remove();
        link = link.enter().append("line").merge(link);
        simulation.nodes(graph.nodes)
                .force("link").links(graph.links);
        simulation.alpha(1).restart();
    }

    // Remove link
    function removeLink(d) {
        if (selectedItem) {
            unselectItem();
            document.getElementById("info-content").innerHTML = "<p>Link <span style=\"color:"
                    + color(d.source.group) + ";\">"
                    + d.source.id + "</span> - <span style=\"color:"
                    + color(d.target.group) + ";\">" + d.target.id
                    + "</span> removed.</p>";
        }
        if (d3.event) {
            d3.event.stopPropagation();
        }
        graph.links = graph.links.filter(function (l) {
            return !(l.source.id === d.source.id && l.target.id === d.target.id);
        });
        directConnections = {};
        graph.links.forEach(function (d) {
            directConnections[d.source.id + "," + d.target.id] = 1;
        });
        link = link.data(graph.links, function (d) {
            return d.source.id + "-" + d.target.id;
        });
        link.exit().remove();
        link = link.enter().append("line").merge(link);
        simulation.force("link").links(graph.links);
        simulation.alpha(1).restart();
    }

    // Select node
    function selectNode(d) {
        if (selectedItem) {
            unselectItem();
        }
        selectedItem = document.getElementById(d.id);
        selectedStroke = "none";
        selectedItem.style["stroke"] = "rgba(0,0,255)";
        document.getElementById(d.id + "-label").style["fill"] = "blue";
        var info = document.getElementById("info-content");
        releaseButton = document.createElement("input");
        zoomButton = document.createElement("input");
        removeButton = document.createElement("input");
        downloadButton = document.createElement("input");
        releaseButton.type = "submit";
        releaseButton.value = "Release node";
        releaseButton.onclick = function () {
            releaseNode(d);
            simulation.alpha(0.3).restart();
        };
        zoomButton.type = "submit";
        zoomButton.value = "Zoom in on node";
        zoomButton.onclick = function () {
            zoomhandler.translateTo(svg, d.x, d.y);
            zoomhandler.scaleTo(svg.transition(), 2);
        };
        removeButton.type = "submit";
        removeButton.value = "Remove node";
        removeButton.onclick = function () {
            removeNode(d);
        };
        downloadButton.type = "submit";
        downloadButton.value = "Download CSV";
        downloadButton.onclick = function () {
          generateCSV(d);
        }

        info.innerHTML = "<h3 style=\"color:" + color(d.group) + ";\">"
                + d.id + " (" + d.hitcount.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".")
                + (d.hitcount !== 1 ? " hits)" : " hit)")
                + "</h3><p>Type: <span style=\"color:" + color(d.group) + ";\">"
                + "Health effect" + "</span></p>"
                + "<p>Also known as:</p>"
                + "<p>PubMed articles:</p>"
                + "<table>"
                + "<tr><th>Title</th><th>Authors</th><th>Date</th></tr>"
                + "<tr><td><a href=\"https://www.ncbi.nlm.nih.gov/pubmed/"
                + 29776004 + "\">"
                + "Knowledge and Health Beliefs about Gestational Diabetes and Healthy Pregnancy's Breastfeeding Intention."
                + "</a></td><td>" + "Park S, Lee JL, In Sun J, Kim Y"
                + "</td><td>" + "2018 May 18" + "</td></tr>"
                + "</table>"
                + "<p><a href=\"http://www.uniprot.org/uniprot/?query="
                + d.id + "&sort=score\">Search UniProt for \"" + d.id +
                "\"</a></p>";
        info.appendChild(releaseButton);
        info.appendChild(zoomButton);
        info.appendChild(removeButton);
        info.appendChild(downloadButton);
    }

    // Select link
    function selectLink(d) {
        if (selectedItem) {
            unselectItem();
            if (focus) {
                toggleFocus(selectedItem);
            }
        }
        var linkId = d.source.id + "-" + d.target.id;
        info = document.getElementById("info-content");
        zoomButton = document.createElement("input");
        removeButton = document.createElement("input");
        downloadButton = document.createElement("input");
        selectedItem = document.getElementById(linkId);
        selectedStroke = "rgba(0,0,0,0.12)";
        selectedItem.style["stroke"] = "rgba(0,0,255,0.5)";
        zoomButton.type = "submit";
        zoomButton.value = "Zoom in on link";
        zoomButton.onclick = function () {
            zoomhandler.translateTo(svg, (d.source.x + d.target.x) / 2, (d.source.y + d.target.y) / 2);
            zoomhandler.scaleTo(svg.transition(), 2);
        };
        removeButton.type = "submit";
        removeButton.value = "Remove link";
        removeButton.onclick = function () {
            removeLink(d);
        };
        downloadButton.type = "submit";
        downloadButton.value = "Download CSV"
        downloadButton.onclick = function () {
          generateCSV(d);
        }
        info.innerHTML = "<h3><span style=\"color:" + color(d.source.group) + ";\">"
                + d.source.id + "</span> - <span style=\"color:"
                + color(d.target.group) + ";\">" + d.target.id
                + "</span></h3><p>Relationship score: " + d.value + "</p>"
                + "<p>Mutual PubMed articles:</p><table>"
                + "<tr><th>Title</th><th>Authors</th><th>Date</th></tr>"
                + "<tr><td><a href=\"https://www.ncbi.nlm.nih.gov/pubmed/"
                + 29776004 + "\">"
                + "Knowledge and Health Beliefs about Gestational Diabetes and Healthy Pregnancy's Breastfeeding Intention."
                + "</a></td><td>" + "Park S, Lee JL, In Sun J, Kim Y"
                + "</td><td>" + "2018 May 18" + "</td></tr>"
                + "</table>";
        info.appendChild(zoomButton);
        info.appendChild(removeButton);
        info.appendChild(downloadButton);
        /* Link focus, incompatible with node focus
         var node = svg.selectAll("circle");
         link = svg.selectAll("line");
         label = svg.selectAll("text");
         if (!focus) {
         node.style("opacity", function(o) {
         return (d.source == o | d.target == o) ? 1 : 0.1;
         });
         label.style("opacity", function(o) {
         return (d.source.id == o.id | d.target.id == o.id) ? 1 : 0.1;
         });
         link.style("opacity", function (o) {
         return d == o ? 1 : 0.1;
         });
         focus = true;
         } else {
         node.style("opacity", 1);
         link.style("opacity", 1);
         label.style("opacity", 1);
         focus = false;
         }*/
    }

    // Release all nodes
    d3.select("#release").on("click", function () {
        node.each(releaseNode);
        simulation.alpha(0.3).restart();
    });

    // Handle drag events
    var draghandler = d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended);

    // Drag events
    function dragstarted(d) {
        if (!d3.event.active)
            simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(d) {
        d.fx = d3.event.x;
        d.fy = d3.event.y;
    }

    function dragended(d) {
        if (!d3.event.active)
            simulation.alphaTarget(0);
        selectNode(d);
    }

    // Get dragsubject
    function dragsubject() {
        return simulation.find(d3.event.x, d3.event.y);
    }

    draghandler(node);
    zoomhandler(svg);

    // Add nodes and links to simulation
    simulation
            .nodes(graph.nodes)
            .on("tick", ticked)
            .force("link")
            .links(graph.links);

    // Update on tick
    function ticked() {
        link
                .attr("x1", function (d) {
                    return d.source.x;
                })
                .attr("y1", function (d) {
                    return d.source.y;
                })
                .attr("x2", function (d) {
                    return d.target.x;
                })
                .attr("y2", function (d) {
                    return d.target.y;
                });

        node.attr("transform", function (d) {
            return "translate(" + d.x + "," + d.y + ")";
        });
    }

    // Create filter button
    var filterDiv = document.getElementById("collapsible");
    filterButton = document.createElement("input");

    filterButton.type = "submit";
    filterButton.value = "Filter";
    filterButton.onclick = function () {
        filterKeywords();
    };

    filterDiv.appendChild(filterButton);

    // Filter the network on keywords
    function filterKeywords() {
        var filters = filterDiv.getElementsByTagName("select");
        keywords = new Set();
        for (var i = 0; i < filters.length; i++) {
            keywords.add(filters[i].value);
        }
        if (focus) {
            toggleFocus(selectedItem);
        }
        if (selectedItem) {
            unselectItem();
        }
        if (highlightedNode) {
            unhighlightNode(highlightedNode);
            highlightedNode = false;
        }
        nodeIds = nodeIds.filter(function (id) {
            if (!keywords.has(id)) {
                document.getElementById(id + "-option").outerHTML = "";
            }
            return keywords.has(id);
        });
        $("#search").autocomplete({source: nodeIds});
        graph.nodes = graph.nodes.filter(function (d) {
            return keywords.has(d.id);
        });
        graph.links = graph.links.filter(function (l) {
            return keywords.has(l.source.id) && keywords.has(l.target.id);
        });
        if (d3.event) {
            d3.event.stopPropagation();
        }
        node = node.data(graph.nodes, function (d) {
            return d.id;
        });
        node.exit().remove();
        node = node.enter().append("circle").attr("fill", function (d) {
            return color(d.group);
        })
                .attr("r", function (d) {
                    return 4 + (d.hitcount / 500000) * 4;
                })
                .merge(node);
        node.select("text").remove();
        node.append("text")
                .attr("dx", 6)
                .attr("id", function (d) {
                    return d.id + "-label";
                })
                .text(function (d) {
                    return d.id;
                });
        link = link.data(graph.links, function (d) {
            return d.source.id + "-" + d.target.id;
        });
        link.exit().remove();
        link = link.enter().append("line").merge(link);
        simulation.nodes(graph.nodes)
                .force("link").links(graph.links);
        simulation.alpha(1).restart();
    }

    // Create search button
    var searchWidget = document.getElementById("search-widget");
    var searchBar = document.getElementById("search");
    searchButton = document.createElement("input");
    var options = document.getElementById("options");

    searchButton.type = "submit";
    searchButton.value = "Search";
    searchButton.onclick = function () {
        search();
    };
    searchBar.onkeydown = function (e) {
        if (e.keyCode === 13) {
            search();
        }
    };
    options.onchange = function () {
        updateSearch();
    };

    searchWidget.appendChild(searchButton);

    // Search function
    function search() {
        if (focus) {
            toggleFocus(selectedItem);
        }
        var query = searchBar.value.toUpperCase();
        foundNode = false;
        otherNodes = svg.selectAll("circle").filter(function (d, i) {
            if (d.id.toUpperCase() === query) {
                foundNode = d;
            }
            return d.id.toUpperCase() !== query;
        });
        if (foundNode) {
            document.getElementById("alert").style["display"] = "none";
            otherNodes.style("opacity", "0.1");
            d3.selectAll(".link").style("opacity", "0.1");
            var label = svg.selectAll("text");
            otherLabels = label.filter(function () {
                return this.innerHTML.toUpperCase() !== query;
            });
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
        searchBar.value = options.value;
        search();
    }

    // Search autocomplete
    $(function () {
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
    $(function () {
        var $dropdown = $("#options");
        $.each(nodeIds, function (key, value) {
            $dropdown.append("<option id=\""
                    + value + "-option\" value=\"" + value + "\">" + value + "</option>");
        });
    });
});

// Handle zoom events
var zoomhandler = d3.zoom()
        .on("zoom", zoomed)
        .scaleExtent([0.1, 15]);

// Network selection variables
var selectedItem = false;
selectedStroke = false;

// Unselect item
function unselectItem() {
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
    document.getElementById(d.id + "-label").style["fill"] = "#00be00";
    highlightedNode.style["stroke"] = "rgba(0,255,0,0.8)";
}

// Unhighlight node
function unhighlightNode(d) {
    if (highlightedNode.id !== selectedItem.id) {
        document.getElementById(d.id + "-label").style["fill"] = "black";
        highlightedNode.style["stroke"] = "none";
    } else {
        document.getElementById(d.id + "-label").style["fill"] = "blue";
        highlightedNode.style["stroke"] = "rgba(0,0,255,0.8)";
    }
}

// Highlight link
function highlightLink(d) {
    if (highlightedLink) {
        unhighlightLink(highlightedLink);
    }
    highlightedLink = document.getElementById(d.source.id + "-" + d.target.id);
    highlightedLink.style["stroke"] = "rgba(0,255,0,0.5)";
}

// Unhighlight link
function unhighlightLink(d) {
    if (highlightedLink !== selectedItem) {
        highlightedLink.style["stroke"] = "rgba(0,0,0,0.12)";
    } else {
        highlightedLink.style["stroke"] = "rgba(0,0,255,0.3)";
    }
}

// Zoom event
function zoomed() {
    if (d3.event.sourceEvent && d3.event.sourceEvent.type === "wheel") {
        g.transition().duration(100).attr("transform", d3.event.transform);
    } else {
        g.attr("transform", d3.event.transform);
    }
}

// Expand or collapse advanced options
function toggleAdvanced() {
    var collapsible = document.getElementById("collapsible");
    toggleAdv = document.getElementById("toggle-advanced");
    if (collapsible.style["display"] === "block") {
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
    span.onclick = function () {
        this.parentNode.outerHTML = "";
    };
    span.innerHTML = "- Remove";
    keywordFilter.innerHTML = document.getElementById("options").innerHTML;
    label.appendChild(span);
    label.appendChild(keywordFilter);
    div.appendChild(label);
}

// Download svg as PNG
function downloadAsPNG() {
    var canvas = document.createElement("canvas");
    a = document.createElement('a');
    xml = (new XMLSerializer()).serializeToString(svg.node());
    xml = xml.replace(/xmlns=\"http:\/\/www\.w3\.org\/2000\/svg\"/, '');
    canvas.width = width;
    canvas.height = height;
    canvg(canvas, xml);
    var dataURL = canvas.toDataURL("image/png");
    dataURL = dataURL.replace(/^data:image\/[^;]*/, "data:application/octet-stream");
    dataURL = dataURL.replace(/^data:application\/octet-stream/, "data:application/octet-stream;headers=Content-Disposition%3A%20attachment%3B%20filename=network.png");
    this.href = dataURL;
}

// Add download event listener to link
document.getElementById("download").addEventListener("click", downloadAsPNG, false);
