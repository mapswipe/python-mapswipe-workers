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
    document.getElementById('geometryContent').innerHTML = ''
    document.getElementById('geometryChangeDetectionContent').innerHTML = ''

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
    element_id = event.target.id + 'Content'

    var reader = new FileReader();
    reader.onload = function(){

      try {
          var text = reader.result;
          var geometry = JSON.parse(text)
          var output = document.getElementById(element_id);
          output.innerHTML = text;
        }
        catch(err) {
          var output = document.getElementById(element_id);
          output.innerHTML = '<b>Error reading GeoJSON file</b><br>' + err;
        }
    };
    reader.readAsText(input.files[0]);
  };
