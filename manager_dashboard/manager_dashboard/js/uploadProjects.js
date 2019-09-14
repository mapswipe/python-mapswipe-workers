var database = firebase.database();
function submitInfo() {

    if (currentUid == null) {
      alert("You are not logged in.");
    } else {

    // get basic project information
    var name = document.getElementById("name").value;
    var lookFor = document.getElementById("lookFor").value;
    var projectDetails = document.getElementById("projectDetails").value;
    var projectType = document.getElementById("projectType").value;
    var image = document.getElementById("image").value;
    var verificationNumber = document.getElementById("verificationNumber").value;
    var createdBy = currentUid;
    var groupSize = document.getElementById("groupSize").value;

    if (projectType == 1) {

        var zoomLevel = document.getElementById("zoomLevel").value;
        var geometry = document.getElementById("geometryContent").innerHTML;
        var tileServer = {
          name: document.getElementById("tileServerBuildArea").value,
          url: document.getElementById("tileServerUrlBuildArea").value,
          wmtsLayerName: document.getElementById("tileServerLayerNameBuildArea").value,
          apiKeyRequired: document.getElementById("apiKeyRequiredBuildArea").value,
          apiKey: document.getElementById("apiKeyBuildArea").value,
          credits: document.getElementById("tileServerCreditsBuildArea").value
        };

        var mapswipe_import = {
            name: name,
            lookFor: lookFor,
            projectDetails: projectDetails,
            projectType: parseInt(projectType),
            image: image,
            verificationNumber: parseInt(verificationNumber),
            groupSize: parseInt(groupSize),
            tileServer: tileServer,
            zoomLevel: parseInt(zoomLevel),
            geometry: JSON.parse(geometry),
            createdBy: createdBy
        }
        console.log(mapswipe_import)

    } else if (projectType == 2) {

        var inputGeometries = document.getElementById("inputGeometries").value;
        var tileServer = {
          name: document.getElementById("tileServerFootprint").value,
          url: document.getElementById("tileServerUrlFootprint").value,
          wmtsLayerName: document.getElementById("tileServerLayerNameFootprint").value,
          caption: document.getElementById("captionFootprint").value,
          date: document.getElementById("dateFootprint").value,
          credits: document.getElementById("tileServerCreditsFootprint").value
        };

        var mapswipe_import = {
            name: name,
            lookFor: lookFor,
            projectDetails: projectDetails,
            projectType: parseInt(projectType),
            image: image,
            groupSize: parseInt(groupSize),
            verificationNumber: parseInt(verificationNumber),
            tileServer: tileServer,
            createdBy: createdBy,
            inputGeometries: inputGeometries
        }

    } else if (projectType == 3) {

      var zoomLevel = document.getElementById("zoomLevelChangeDetection").value;
      var geometry = document.getElementById("geometryChangeDetectionContent").innerHTML;
      var tileServerA = {
        name: document.getElementById("tileServerChangeDetectionA").value,
        url: document.getElementById("tileServerUrlChangeDetectionA").value,
        wmtsLayerName: document.getElementById("tileServerLayerNameChangeDetectionA").value,
        apiKeyRequired: document.getElementById("apiKeyRequiredChangeDetectionA").value,
        apiKey: document.getElementById("apiKeyChangeDetectionA").value,
        caption: document.getElementById("captionChangeDetectionA").value,
        date: document.getElementById("dateChangeDetectionA").value,
        credits: document.getElementById("tileServerCreditsChangeDetectionA").value
      };
      var tileServerB = {
        name: document.getElementById("tileServerChangeDetectionB").value,
        url: document.getElementById("tileServerUrlChangeDetectionB").value,
        wmtsLayerName: document.getElementById("tileServerLayerNameChangeDetectionB").value,
        apiKeyRequired: document.getElementById("apiKeyRequiredChangeDetectionB").value,
        apiKey: document.getElementById("apiKeyChangeDetectionB").value,
        caption: document.getElementById("captionChangeDetectionB").value,
        date: document.getElementById("dateChangeDetectionB").value,
        credits: document.getElementById("tileServerCreditsChangeDetectionB").value
      };

      var mapswipe_import = {
          name: name,
          lookFor: lookFor,
          projectDetails: projectDetails,
          projectType: parseInt(projectType),
          image: image,
          groupSize: parseInt(groupSize),
          verificationNumber: parseInt(verificationNumber),
          tileServerA: tileServerA,
          tileServerB: tileServerB,
          zoomLevel: parseInt(zoomLevel),
          geometry: JSON.parse(geometry),
          createdBy: createdBy
      }

    }

    firebase.database().ref('v2/projectDrafts/').push().set(mapswipe_import)
          .then(function() {
            clear_all_fields();
            displaySuccessMessage();
          })
          .catch(function(error) {
            alert('could not upload data: ' + error);
          });

  }
}
