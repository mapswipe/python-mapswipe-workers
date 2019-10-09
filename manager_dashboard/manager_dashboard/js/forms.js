//auto expand textarea
function adjust_textarea(h) {
    h.style.height = "20px";
    h.style.height = (h.scrollHeight)+"px";
}

function displayProjectTypeFormular(projectType) {
    if (projectType == 1) {
        document.getElementById("BuildAreaProjectFormular").style.display = "block";
        document.getElementById("FootprintProjectFormular").style.display = "None",
        document.getElementById("ChangeDetectionProjectFormular").style.display = "None";
        document.getElementById("tileServerBuildArea").value = "bing";
        displayTileServer ("bing", "BuildArea", "");
        setTimeout(function(){ BuildAreaMap.invalidateSize()}, 400);
    } else if (projectType == 2) {
        document.getElementById("FootprintProjectFormular").style.display = "block";
        document.getElementById("BuildAreaProjectFormular").style.display = "None";
        document.getElementById("ChangeDetectionProjectFormular").style.display = "None";
        document.getElementById("tileServerFootprint").value = "bing";
        displayTileServer ("bing", "Footprint", "");
    } else if (projectType == 3) {
      document.getElementById("FootprintProjectFormular").style.display = "None"
      document.getElementById("BuildAreaProjectFormular").style.display = "None";
      document.getElementById("ChangeDetectionProjectFormular").style.display = "block";
      document.getElementById("tileServerChangeDetectionA").value = "bing";
      document.getElementById("tileServerChangeDetectionB").value = "bing";
      displayTileServer ("bing", "ChangeDetectionA", "");
      displayTileServer ("bing", "ChangeDetectionB", "");
      setTimeout(function(){ ChangeDetectionMap.invalidateSize()}, 400);
  }
}

function displayTileServer (t, projectType, which) {
    tileServer = t.value
    if (tileServer == "custom") {
        document.getElementById("tileServerUrlField"+projectType+which).style.display = "block"
        document.getElementById("tileServerLayerNameField"+projectType+which).style.display = "block";
    } else if (tileServer == "sinergise") {
        document.getElementById("tileServerUrlField"+projectType+which).style.display = "None";
        document.getElementById("tileServerLayerNameField"+projectType+which).style.display = "block";
    } else {
        document.getElementById("tileServerUrlField"+projectType+which).style.display = "None";
        document.getElementById("tileServerLayerNameField"+projectType+which).style.display = "None";
    }
}

function clear_all_fields() {
    forms = document.getElementsByClassName('form-style-7')
    for (i = 0; i < forms.length; i++) {
      forms[i].reset()
    }
    document.getElementById('geometryInfo').innerHTML = ''
    document.getElementById('geometryContent').innerHTML = ''
    BuildAreaLayer.clearLayers()
    document.getElementById('geometryChangeDetectionInfo').innerHTML = ''
    document.getElementById('geometryChangeDetectionContent').innerHTML = ''
    ChangeDetectionLayer.clearLayers()
    document.getElementById('imageText').innerHTML = ''
    document.getElementById('imageFile').src = ''
    displayProjectTypeFormular(1)
  }

function displaySuccessMessage() {
  //document.getElementById("import-formular").style.display = "None";
  alert('Your project has been uploaded. It can take up to one hour for the project to appear in the dashboard.')
}

function displayImportForm() {
  document.getElementById("import-formular").style.display = "block";
}

function openFile(event) {
    var input = event.target;
    var info_element_id = event.target.id + 'Info'
    var content_element_id = event.target.id + 'Content'
    var map_element_id = event.target.id + 'Map'

    var info_output = document.getElementById(info_element_id);
    info_output.innerHTML = '';
    info_output.style.display = 'block'

    var content_output = document.getElementById(content_element_id);

    if (event.target.id === 'geometry') {
      var map = BuildAreaMap
      var layer = BuildAreaLayer
      var zoomLevel = parseInt(document.getElementById('zoomLevel').value)
    } else {
      var map = ChangeDetectionMap
      var layer = ChangeDetectionLayer
      var zoomLevel = parseInt(document.getElementById('zoomLevelChangeDetection').value)
    }

    var reader = new FileReader();
    reader.onload = function(){

      try {
          var text = reader.result;
          var geojsonData = JSON.parse(text)

          // check number of features
          numberOfFeatures = geojsonData['features'].length
          console.log('number of features: ' + numberOfFeatures)
          if (numberOfFeatures > 1) {
            throw 'too many features: ' + numberOfFeatures
          }
          info_output.innerHTML += 'Number of Features: ' + numberOfFeatures + '<br>';
          info_output.style.display = 'block'

          // check input geometry type
          feature = geojsonData['features'][0]
          type = turf.getType(feature)
          console.log('geometry type: ' + type)
          if (type !== 'Polygon' & type !== 'MultiPolygon') {
            throw 'wrong geometry type: ' + type
          }
          info_output.innerHTML += 'Feature Type: ' + type + '<br>';
          info_output.style.display = 'block'

          // check project size

          area = turf.area(feature)/1000000 // area in square kilometers
          maxArea = (20 - zoomLevel) * (20 - zoomLevel) * 1250
          console.log('project size: ' + area + ' sqkm')
          if (area > 5000) {
            throw 'project is to large: ' + area + ' sqkm; ' + 'max allowed size for this zoom level: ' + maxArea + ' sqkm'
          }
          info_output.innerHTML += 'Project Size: ' + area + ' sqkm<br>';
          info_output.style.display = 'block'

          // add feature to map
          layer.clearLayers()
          layer.addData(geojsonData);
          map.fitBounds(layer.getBounds());
          console.log('added input geojson feature')

          // add text to html object
          info_output.innerHTML += 'Project seems to be valid :)';
          info_output.style.display = 'block'

          if (event.target.id === 'geometry') {
            BuildAreaGeometry = text
          } else {
            ChangeDetectionGeometry = text
          }


        }
        catch(err) {
          info_output.innerHTML = '<b>Error reading GeoJSON file</b><br>' + err;
          info_output.style.display = 'block'
        }
    };
    reader.readAsText(input.files[0]);
  };

function openImageFile(event) {
    var input = event.target;
    element_id = event.target.id + 'File'

    var reader = new FileReader();
    reader.onload = function(){
      try {
        var dataURL = reader.result;
        var output = document.getElementById(element_id);
        output.src = dataURL;
      }
      catch(err) {
          element_id = event.target.id + 'Text'
          var output = document.getElementById(element_id);
          output.innerHTML = '<b>Error reading Image file</b><br>' + err;
        }
    };
    reader.readAsDataURL(input.files[0]);
  };

function initMap() {
  BuildAreaMap = L.map('geometryMap').setView([0.0, 0.0], 4);
  L.tileLayer( 'https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    subdomains: ['a','b','c']
  }).addTo( BuildAreaMap );
  console.log('added map');
  BuildAreaLayer = L.geoJSON().addTo(BuildAreaMap);
  setTimeout(function(){ BuildAreaMap.invalidateSize()}, 400);

  ChangeDetectionMap = L.map('geometryChangeDetectionMap').setView([0.0, 0.0], 4);
  L.tileLayer( 'https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    subdomains: ['a','b','c']
  }).addTo( ChangeDetectionMap );
  console.log('added map');
  ChangeDetectionLayer = L.geoJSON().addTo(ChangeDetectionMap);
  setTimeout(function(){ ChangeDetectionMap.invalidateSize()}, 400);
  }