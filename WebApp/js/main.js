var category = $("#options_id").val();
var currentCategory = $("#options_id").val();
var price = $("#options_price").val() || 'On';
var quantity = $("#options_quantity").val() || 'On';
var days = $("#options_days").val() || 'On';
var subscription = $("#options_subscription").val() || 'On';
var max = 0;
var min = 999999;

// Initialize option start
var selectCategoryID = document.getElementById("options_id");
$.getJSON( "data/category_id.json", function( data ) {
  $.each( data, function( key, val ) {
    var opt = document.createElement('option');
    opt.value = val["id"];
    opt.id = val["id"];
    opt.innerHTML = val["id"];
    selectCategoryID.appendChild(opt);
  });
});

// harusnya select name
var selectCategoryName = document.getElementById("options_name");
$.getJSON( "data/category_name.json", function( data ) {
  $.each( data, function( key, val ) {
    var opt = document.createElement('option');
    opt.value = val["id"];
    opt.id = "name_"+val["id"];
    opt.innerHTML = ""+val["name"]+" - "+val["id"];
    selectCategoryName.appendChild(opt);
  });
});
// Initialize option end

// For radio start
$(function() {
  $('input[name=category_radio]').on('click init-post-format', function() {
    $('#select_id').toggle($('#category_id_radio').prop('checked'));
  }).trigger('init-post-format');
});

$(function() {
  $('input[name=category_radio]').on('click init-post-format', function() {
    $('#select_name').toggle($('#category_name_radio').prop('checked'));
  }).trigger('init-post-format');
});
// For radio end

// Select option start
$('#choose_id').click(function (e) {
  e.stopPropagation();
  $('#options_id').toggle();
});

$('#options_id').change(function (e) {
  e.stopPropagation();
  var val = this.value || 'Select options';
  $(this).siblings('#choose_id').text(val);
  category = $( "#options_id" ).val();
  $(this).hide();
});

$('#choose_name').click(function (e) {
  e.stopPropagation();
  $('#options_name').toggle();
});

$('#options_name').change(function (e) {
  e.stopPropagation();
  var val = this.value || 'Select options';
  $(this).siblings('#choose_name').text(document.getElementById("name_"+val).innerHTML);
  category = $( "#options_name" ).val();
  $(this).hide();
});

$('#choose_price').click(function (e) {
  e.stopPropagation();
  $('#options_price').toggle();
});

$('#options_price').change(function (e) {
  e.stopPropagation();
  var val = this.value || 'On';
  $(this).siblings('#choose_price').text(val);
  price = $( "#options_price" ).val();
  $(this).hide();
});

$('#choose_quantity').click(function (e) {
  e.stopPropagation();
  $('#options_quantity').toggle();
});

$('#options_quantity').change(function (e) {
  e.stopPropagation();
  var val = this.value || 'On';
  $(this).siblings('#choose_quantity').text(val);
  quantity = $( "#options_quantity" ).val();
  $(this).hide();
});

$('#choose_days').click(function (e) {
  e.stopPropagation();
  $('#options_days').toggle();
});

$('#options_days').change(function (e) {
  e.stopPropagation();
  var val = this.value || 'On';
  $(this).siblings('#choose_days').text(val);
  days = $( "#options_days" ).val();
  $(this).hide();
});

$('#choose_subscription').click(function (e) {
  e.stopPropagation();
  $('#options_subscription').toggle();
});

$('#options_subscription').change(function (e) {
  e.stopPropagation();
  var val = this.value || 'On';
  $(this).siblings('#choose_subscription').text(val);
  subscription = $( "#options_subscription" ).val();
  $(this).hide();
});
  
$('select').find('option').on({
  'mouseover': function () {
    $('.hover').removeClass('hover');
    $(this).addClass('hover');
  },
    'mouseleave': function () {
    $(this).removeClass('hover');
  }
});
// Select option end

function refresh() {
  $('#options_id').siblings('#choose_id').text(currentCategory);
  $('#options_name').siblings('#choose_name').text(currentCategory);
  var explanation = document.getElementById("explanation");
  var parent = document.getElementById("content_graph");
  var child = document.getElementById("graph");
  parent.removeChild(child);
  var div = document.createElement('div');
  div.className = "graph";
  div.id = 'graph';
  var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("width", '900');
  svg.setAttribute("height", '600');
  div.appendChild(svg);
  parent.insertBefore(div, explanation);
  setMinMax(category,price,quantity,days,subscription);
  buildGraph(currentCategory);
  buildExplanation(currentCategory);
}

function build() {
  currentCategory = category;
  var explanation = document.getElementById("explanation");
  var parent = document.getElementById("content_graph");
  var child = document.getElementById("graph");
  parent.removeChild(child);
  var div = document.createElement('div');
  div.className = "graph";
  div.id = 'graph';
  var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("width", '900');
  svg.setAttribute("height", '600');
  div.appendChild(svg);
  parent.insertBefore(div, explanation);

  setMinMax(category,price,quantity,days,subscription);
  
  buildGraph(category,price,quantity,days,subscription);

  buildExplanation(category,price,quantity,days,subscription);
}

function buildGraph(category,price,quantity,days,subscription) {
  //create somewhere to put the force directed graph
  var svg = d3.select("svg"),
      width = +svg.attr("width"),
      height = +svg.attr("height");
  // var radius = 10; 

  //set up the simulation and add forces  
  filename = "data/"+category+".0";
  if (price == 'On') { 
    filename += "_p";
  }
  if (quantity == 'On') { 
    filename += "_q";
  }
  if (subscription == 'On') { 
    filename += "_s";
  }
  if (days == 'On') { 
    filename += "_d";
  }
  filename += ".d3.json";
<<<<<<< HEAD
  alert(filename);
=======
>>>>>>> firsttry-dengraph
  d3.json(filename, function(error, data) {
    var simulation = d3.forceSimulation()
              .nodes(data.nodes);
                                  
    var link_force =  d3.forceLink(data.links)
                            .id(function(d) { return d.id; })
                            .distance(distance);
       
    var charge_force = d3.forceManyBody()
        .strength(-15); 
        
    var center_force = d3.forceCenter(width / 2, height / 2);  
                          
    simulation
        .force("charge_force", charge_force)
        .force("center_force", center_force)  
        .force("links",link_force)
     ;

    //add tick instructions: 
    simulation.on("tick", tickActions );

    //add encompassing group for the zoom 
    var g = svg.append("g")
        .attr("class", "everything");

    svg.append("svg:defs").selectAll("marker")
    .data(["end"])      // Different link/path types can be defined here
  .enter().append("svg:marker")    // This section adds in the arrows
    .attr("id", String)
    .attr("viewBox", "0 -5 10 10")
    .attr("refX", 15)
    .attr("refY", 0.5)
    .attr("markerWidth", 5)
    .attr("markerHeight", 5)
    .attr("orient", "auto")
  .append("svg:path")
    .attr("d", "M0,-5L10,0L0,5");

    //draw lines for the links 
    var link = g.append("g")
          .attr("marker-end", "url(#end)")
          .attr("class", "links")
        .selectAll("line")
        .data(data.links)
        .enter().append("line")
          .attr("stroke-width", 2)
          .style("stroke", linkColour);        

    //draw circles for the nodes 
    var node = g.append("g")
            .attr("class", "nodes") 
            .selectAll("circle")
            .data(data.nodes)
            .enter()
            .append("circle")
            .attr("r", circleRadius)
            .attr("fill", circleColour);
    
    node.append("title")
    .text(nodeDescription);

    //add drag capabilities  
    var drag_handler = d3.drag()
      .on("start", drag_start)
      .on("drag", drag_drag)
      .on("end", drag_end); 
      
    drag_handler(node);


    //add zoom capabilities 
    var zoom_handler = d3.zoom()
        .on("zoom", zoom_actions);

    zoom_handler(svg); 

    /** Functions **/

    //Function to choose what color circle we have
    //Let's return blue for males and red for females
    function circleColour(d){
      if (d.cluster == null) {
        return "rgb(0, 0, 0)";
      } else {
        distancePerCluster = Math.floor(255*255*255/200);
        clusterColor = (d.cluster+1) * distancePerCluster;
        hexString = clusterColor.toString(16);
        for (i=0;i<(6-hexString.length);i++){
          hexString = "0"+hexString;
        }
        return "#"+hexString;   
      }
    }

    function circleRadius(d){
<<<<<<< HEAD
      if ((d.harmonic/50) > 10) {
        return 15;
      } else {
        return 5 + Math.floor(d.harmonic/50);
=======
      if ((d.closeness/50) > 10) {
        return 15;
      } else {
        return 5 + Math.floor(d.closeness/50);
>>>>>>> firsttry-dengraph
      }
    }

    function distance(d){
      //range 1-10
      dist = (((d.distance-min)/(max-min))*9)+1;
      //range 30-120
      return 20+(dist*10);
    }

    function nodeDescription(d) {
      desc = "ID : "+d.id;
<<<<<<< HEAD
      desc += "\n Cluster : ";
      if (d.cluster != null) {
        desc += d.cluster;
      } else {
        desc += "none";
      }
      desc += "\n Rate Out : "+d.degree_out;
      desc += "\n Harmonic : "+d.harmonic;
      desc += "\n Remitted : ";
      if (d.remitted != null) {
        desc += d.remitted;
      } else {
        desc += "none";
      }
      desc += "\n Refunded : ";
      if (d.refunded != null) {
        desc += d.refunded;
      } else {
        desc += "none";
      }
      desc += "\n Refund Rate : ";
      if (d.refundRate != null) {
        desc += d.refundRate;
      } else {
        desc += "none";
      }
=======
      desc += "\n Cluster : "
      if (d.cluster != null) {
        desc += d.cluster;
      } else {
        desc += "none"
      }
      desc += "\n Rate Out : "+d.rate_out;
      desc += "\n Closeness : "+d.closeness;
>>>>>>> firsttry-dengraph
      return desc;
    }

    //Function to choose the line colour and thickness 
    //If the link type is "A" return green 
    //If the link type is "E" return red 
    function linkColour(d){
      return "#535353";
    }

    //Drag functions 
    //d is the node 
    function drag_start(d) {
     if (!d3.event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    //make sure you can't drag the circle outside the box
    function drag_drag(d) {
      d.fx = d3.event.x;
      d.fy = d3.event.y;
    }

    function drag_end(d) {
      if (!d3.event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }

    //Zoom functions 
    function zoom_actions(){
        g.attr("transform", d3.event.transform)
    }

    function tickActions() {
        //update circle positions each tick of the simulation 
<<<<<<< HEAD
        node
=======
           node
>>>>>>> firsttry-dengraph
            .attr("cx", function(d) { return d.x; })
            .attr("cy", function(d) { return d.y; });
            
        //update link positions 
        link
            .attr("x1", function(d) { return d.source.x; })
            .attr("y1", function(d) { return d.source.y; })
            .attr("x2", function(d) { return d.target.x; })
            .attr("y2", function(d) { return d.target.y; });
    } 
  });    
}

function buildExplanation(category,price,quantity,days,subscription) {
  filename = "data/"+category+".0";
  if (price == 'On') { 
    filename += "_p";
  }
  if (quantity == 'On') { 
    filename += "_q";
  }
  if (subscription == 'On') { 
    filename += "_s";
  }
  if (days == 'On') { 
    filename += "_d";
  }
  filename += ".d3.json";
  var parent = document.getElementById("explanation");
  var child = document.getElementById("graph_detail");
  parent.removeChild(child);
  var graph_detail = document.createElement('div');
  graph_detail.id = "graph_detail";
  parent.appendChild(graph_detail);
  $.getJSON( filename, function( data ) {
    var items = [];
    ci = document.getElementById("category_id");
    ci.innerHTML = "Category ID : "+category;
    cn = document.getElementById("category_name");
    cn.innerHTML = "Category Name : "+document.getElementById("name_"+category).innerHTML.split("-")[0]
    price = document.getElementById("price");
    price.innerHTML = "Price : "+data["P"];
    quantity = document.getElementById("quantity");
    quantity.innerHTML = "Quantity : "+data["Q"];
    nf = document.getElementById("nf");
    nf.innerHTML = "Normalization Function : "+data["QPF"];
    tf = document.getElementById("tf");
    tf.innerHTML = "Time Function : "+data["TF"];
    df = document.getElementById("df");
    df.innerHTML = "Days Function : "+data["DF"];
    sf = document.getElementById("sf");
    sf.innerHTML = "Subscription Factor : "+data["SF"];
    md = document.getElementById("md");
    md.innerHTML = "Maximal Distance : "+data["MD"];
    mn = document.getElementById("mn");
    mn.innerHTML = "Minimal Neighbor : "+data["MN"];
    mc = document.getElementById("mc");
    mc.innerHTML = "Minimal Harmonic : "+data["MH"];
    $.each( data["Cluster"], function( key, val ) {
      var div = document.createElement('div');
      div.className = "cluster";
      html = "<span>No Cluster : "+key+"</span><br>\n<span>Number of Core : "+val["CORE"].length+"</span><br>\n<span>Core : "+val["CORE"][0];
      for (i=1;i<val["CORE"].length;i++) {
        html += ", "+val["CORE"][i];
      }
      html += "</span><br>\n<span>Number of Neighbor : "+val["NEIGHBOR"].length+"</span><br>\n<span>Neighbor : "+val["NEIGHBOR"][0];
      for (i=1;i<val["NEIGHBOR"].length;i++) {
        html += ", "+val["NEIGHBOR"][i];
      }
      html += "</span><br>\n<span>Remitted Transaction : "+val["remitted"];
      html += "</span><br>\n<span>Refunded Transaction : "+val["refunded"];
	  html += "</span><br>\n<span>Refund Rate Transaction : "+val["refundRate"];
      html += "</span><br><br>\n";
      div.innerHTML = html;
      graph_detail.appendChild(div);
    });
  });
}

function setMinMax(category,price,quantity,days,subscription) {
  filename = "data/"+category+".0";
  if (price == 'On') { 
    filename += "_p";
  }
  if (quantity == 'On') { 
    filename += "_q";
  }
  if (subscription == 'On') { 
    filename += "_s";
  }
  if (days == 'On') { 
    filename += "_d";
  }
  filename += ".d3.json";
  max = 0;
  min = 999999;
  $.getJSON( filename, function( data ) {
    $.each( data["links"], function( key, val ) {
      if (val["distance"] > max) {
        max = val["distance"];
      }
      if (val["distance"] < min) {
        min = val["distance"];
      }
    });
  });
}

