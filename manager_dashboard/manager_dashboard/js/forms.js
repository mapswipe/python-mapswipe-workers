//auto expand textarea
function adjust_textarea(h) {
    h.style.height = "20px";
    h.style.height = (h.scrollHeight)+"px";
}

function initForm() {
    initMap();
    displayProjectTypeForm("build_area")
}


function initMap() {
  ProjectAoiMap = L.map('geometryMap').setView([0.0, 0.0], 4);
  L.tileLayer( 'https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    subdomains: ['a','b','c']
  }).addTo( ProjectAoiMap );
  console.log('added map');
  aoiLayer = L.geoJSON().addTo(ProjectAoiMap);
  setTimeout(function(){ ProjectAoiMap.invalidateSize()}, 400);

  }

function displayProjectTypeForm(projectType) {
    document.getElementById("projectType").value = projectType;
    switch (projectType) {
        case "build_area":
            displayTileServer("bing", "A");
            document.getElementById("groupSize").value = 120;
            document.getElementById("form_project_aoi_geometry").style.display = "block";
            document.getElementById("form_project_task_geometry").style.display = "None";
            document.getElementById("form_zoom_level").style.display = "block";
            document.getElementById("form_tile_server_a").style.display = "block";
            document.getElementById("form_tile_server_b").style.display = "None";
            setTimeout(function(){ ProjectAoiMap.invalidateSize()}, 400);
            break;
        case "footprint":
            displayTileServer("bing", "A");
            document.getElementById("groupSize").value = 25;
            document.getElementById("form_project_aoi_geometry").style.display = "None";
            document.getElementById("form_project_task_geometry").style.display = "block";
            document.getElementById("form_zoom_level").style.display = "None";
            document.getElementById("form_tile_server_a").style.display = "block";
            document.getElementById("form_tile_server_b").style.display = "None";
            break;
        case "change_detection":
        case "completeness":
            displayTileServer("bing", "A");
            displayTileServer("bing", "B");
            if (projectType == "change_detection") {
                document.getElementById("groupSize").value = 25;
            } else {
                document.getElementById("groupSize").value = 80;
            }
            document.getElementById("form_project_aoi_geometry").style.display = "block";
            document.getElementById("form_project_task_geometry").style.display = "None";
            document.getElementById("form_zoom_level").style.display = "block";
            document.getElementById("form_tile_server_a").style.display = "block";
            document.getElementById("form_tile_server_b").style.display = "block";
            setTimeout(function(){ ProjectAoiMap.invalidateSize()}, 400);
            break;
    }
}

function addTileServerCredits (tileServerName, which) {
    var credits = {
        "bing": "© 2019 Microsoft Corporation, Earthstar Geographics SIO",
        "maxar_premium": "© 2019 Maxar",
        "maxar_standard": "© 2019 Maxar",
        "esri": "© 2019 ESRI",
        "esri_beta": "© 2019 ESRI",
        "mapbox": "© 2019 MapBox",
        "sinergise": "© 2019 Sinergise",
        "custom": "Please add imagery credits here."
    }
    document.getElementById("tileServer"+which+"Credits").value = credits[tileServerName]
}


function displayTileServer (tileServerName, which) {
    switch (tileServerName) {
        case "custom":
            document.getElementById("tileServer"+which+"UrlField").style.display = "block";
            document.getElementById("tileServer"+which+"LayerNameField").style.display = "block";
            break;
        case "sinergise":
            document.getElementById("tileServer"+which+"UrlField").style.display = "None";
            document.getElementById("tileServer"+which+"LayerNameField").style.display = "block";
            break;
        default:
            document.getElementById("tileServer"+which+"UrlField").style.display = "None";
            document.getElementById("tileServer"+which+"LayerNameField").style.display = "None";
    }
    addTileServerCredits(tileServerName, which)
}


function clear_fields() {
    console.log('clear fields.')
    document.getElementById('projectNumber').value = 1
    document.getElementById('inputAoi').value = null
    document.getElementById('geometryInfo').innerHTML = ''
    document.getElementById('geometryContent').innerHTML = ''
    aoiLayer.clearLayers()
    displayProjectTypeForm("build_area")
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

    // clear info field
    var info_output = document.getElementById("geometryInfo");
    info_output.innerHTML = '';
    info_output.style.display = 'block'

    // clear map layers
    aoiLayer.clearLayers()

    // Check file size before loading
    var filesize = input.files[0].size;
    if (filesize > 1 * 1024 * 1024) {
      var err='filesize is too big (max 1MB): ' + filesize/(1000*1000)
      info_output.innerHTML = '<b>Error reading GeoJSON file</b><br>' + err;
      info_output.style.display = 'block'
    } else {
      info_output.innerHTML += 'File Size is valid <br>';
      info_output.style.display = 'block'

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

              // check project size, based on zoom level
              var zoomLevel = parseInt(document.getElementById('zoomLevel').value);
              area = turf.area(feature)/1000000 // area in square kilometers
              maxArea = (23 - zoomLevel) * (23 - zoomLevel) * 200
              console.log('project size: ' + area + ' sqkm')
              if (area > maxArea) {
                throw 'project is to large: ' + area + ' sqkm; ' + 'max allowed size for this zoom level: ' + maxArea + ' sqkm'
              }
              info_output.innerHTML += 'Project Size: ' + area + ' sqkm<br>';
              info_output.style.display = 'block'

              // add feature to map
              aoiLayer.addData(geojsonData);
              ProjectAoiMap.fitBounds(aoiLayer.getBounds());
              console.log('added input geojson feature')

              // add text to html object
              info_output.innerHTML += 'Project seems to be valid :)';
              info_output.style.display = 'block'

              // set project aoi geometry
              projectAoiGeometry = text
            }
            catch(err) {
              info_output.innerHTML = '<b>Error reading GeoJSON file</b><br>' + err;
              info_output.style.display = 'block'
            }
        };
    reader.readAsText(input.files[0]);
    }
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


function closeModal() {
    var modal = document.getElementById("uploadModal");
    modal.style.display = "none";
    var modalSuccess = document.getElementById("modalSuccess");
    modalSuccess.style.display = "none";
}
