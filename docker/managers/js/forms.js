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
        document.getElementById("apiKeyRequiredField"+projectType+which).style.display = "block";
        document.getElementById("apiKeyField"+projectType+which).style.display = "block";
    } else if (tileServer == "sinergise") {
        document.getElementById("tileServerUrlField"+projectType+which).style.display = "None";
        document.getElementById("tileServerLayerNameField"+projectType+which).style.display = "block";
        document.getElementById("apiKeyRequiredField"+projectType+which).style.display = "None";
        document.getElementById("apiKeyField"+projectType+which).style.display = "None";
    } else {
        document.getElementById("tileServerUrlField"+projectType+which).style.display = "None";
        document.getElementById("tileServerLayerNameField"+projectType+which).style.display = "None";
        document.getElementById("apiKeyRequiredField"+projectType+which).style.display = "None";
        document.getElementById("apiKeyField"+projectType+which).style.display = "None";
    }
}

function clear_all_fields() {
    forms = document.getElementsByClassName('form-style-7')
    for (i = 0; i < forms.length; i++) {
      forms[i].reset()
    }
    displayProjectTypeFormular(1)
  }

function displaySuccessMessage() {
  document.getElementById("success-message").style.display = "block";
  document.getElementById("import-formular").style.display = "None";
}

function displayImportForm() {
  document.getElementById("success-message").style.display = "None";
  document.getElementById("import-formular").style.display = "block";
}
