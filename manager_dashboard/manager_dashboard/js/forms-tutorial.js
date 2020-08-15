//auto expand textarea
function adjust_textarea(h) {
    h.style.height = "20px";
    h.style.height = (h.scrollHeight)+"px";
}

function initForm() {
    displayProjectTypeForm("build_area")
}



function displayProjectTypeForm(projectType) {
    document.getElementById("projectType").value = projectType;
    switch (projectType) {
        case "build_area":
            displayTileServer("bing", "A");
            document.getElementById("form_zoom_level").style.display = "block";
            document.getElementById("form_tile_server_a").style.display = "block";
            document.getElementById("form_tile_server_b").style.display = "None";
            break;
        case "footprint":
            displayTileServer("bing", "A");
            document.getElementById("form_zoom_level").style.display = "None";
            document.getElementById("form_tile_server_a").style.display = "block";
            document.getElementById("form_tile_server_b").style.display = "None";
            break;
        case "change_detection":
        case "completeness":
            displayTileServer("bing", "A");
            displayTileServer("bing", "B");
            document.getElementById("form_zoom_level").style.display = "block";
            document.getElementById("form_tile_server_a").style.display = "block";
            document.getElementById("form_tile_server_b").style.display = "block";
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
    displayProjectTypeForm("build_area")
  }

function displaySuccessMessage() {
  //document.getElementById("import-formular").style.display = "None";
  alert('Your project has been uploaded. It can take up to one hour for the project to appear in the dashboard.')
}

function displayImportForm() {
  document.getElementById("import-formular").style.display = "block";
}

function openJsonFile(event) {
    var input = event.target;

    // clear info field
    var info_output = document.getElementById("screenInfo");
    info_output.innerHTML = '';
    info_output.style.display = 'block'

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
              var screensJsonData = JSON.parse(text)
              // check number of screens
              numberOfScreens = Object.keys(screensJsonData).length
              console.log('number of screens: ' + numberOfScreens)

              info_output.innerHTML += 'Number of Screens: ' + numberOfScreens + '<br>';
              info_output.style.display = 'block'
              screens = text

            }
            catch(err) {
              info_output.innerHTML = '<b>Error reading JSON file</b><br>' + err;
              info_output.style.display = 'block'
            }
        };
    reader.readAsText(input.files[0]);
    }
  };

function openGeoJsonFile(event) {
    var input = event.target;

    // clear info field
    var info_output = document.getElementById("tutorialTasksInfo");
    info_output.innerHTML = '';
    info_output.style.display = 'block'

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
              var geoJsonData = JSON.parse(text)
              // check number of screens
              numberOfFeatures = Object.keys(geoJsonData["features"]).length
              console.log('number of features: ' + numberOfFeatures)

              info_output.innerHTML += 'Number of Features: ' + numberOfFeatures + '<br>';
              info_output.style.display = 'block'
              tutorialTasks = text

            }
            catch(err) {
              info_output.innerHTML = '<b>Error reading GeoJSON file</b><br>' + err;
              info_output.style.display = 'block'
            }
        };
    reader.readAsText(input.files[0]);
    }
  };


function closeModal() {
    var modal = document.getElementById("uploadModal");
    modal.style.display = "none";
    var modalSuccess = document.getElementById("modalSuccess");
    modalSuccess.style.display = "none";
}
