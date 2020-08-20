var database = firebase.database();


function getFormInput() {
    var form_data = {
        lookFor: document.getElementById("lookFor").value,
        createdBy: currentUid
    }

    // add project type specific attributes
    projectType = document.getElementById("projectType").value
    switch (projectType) {
        case "build_area":
            form_data.projectType = 1;
            form_data.zoomLevel = parseInt(document.getElementById("zoomLevel").value);
            form_data.tileServer = {
              name: document.getElementById("tileServerAName").value,
              url: document.getElementById("tileServerAUrl").value,
              wmtsLayerName: document.getElementById("tileServerALayerName").value,
              credits: document.getElementById("tileServerACredits").value
            };
            break;
        case "footprint":
            form_data.projectType = 2;
            form_data.tileServer = {
              name: document.getElementById("tileServerAName").value,
              url: document.getElementById("tileServerAUrl").value,
              wmtsLayerName: document.getElementById("tileServerALayerName").value,
              credits: document.getElementById("tileServerACredits").value
            };
            break;
        case "change_detection":
        case "completeness":
            if (projectType == "change_detection") {
                form_data.projectType = 3;
            } else {
                form_data.projectType = 4;
            }
            form_data.zoomLevel = parseInt(document.getElementById("zoomLevel").value);
            form_data.tileServer = {
              name: document.getElementById("tileServerAName").value,
              url: document.getElementById("tileServerAUrl").value,
              wmtsLayerName: document.getElementById("tileServerALayerName").value,
              credits: document.getElementById("tileServerACredits").value
            };
            form_data.tileServerB = {
              name: document.getElementById("tileServerBName").value,
              url: document.getElementById("tileServerBUrl").value,
              wmtsLayerName: document.getElementById("tileServerBLayerName").value,
              credits: document.getElementById("tileServerBCredits").value
            };
            break;
    }

    form_data.screens = JSON.parse(screens)
    form_data.tutorialTasks = JSON.parse(tutorialTasks)

    form_data.name = projectType + '_tutorial_' + form_data.lookFor
    return form_data
}

function upload_to_firebase() {
    switch (currentUid) {
        case null:
            alert("You are not logged in.");
        default:
            var modal = document.getElementById("uploadModal");
            modal.style.display = "block";
            var modalOngoing = document.getElementById("modalOngoing");
            modalOngoing.style.display = "block";

            var modal = document.getElementById("uploadModal");
            modal.style.display = "block";

            // get form data
            // TODO: add checks if all input values are valid, e.g. image available
            mapswipe_import = getFormInput()

            // TODO: unwrap this here and use separate function and await
            firebase.database().ref('v2/tutorialDrafts/').push().set(mapswipe_import)
              .then(function() {
                clear_fields();
                var modalOngoing = document.getElementById("modalOngoing");
                modalOngoing.style.display = "none";
                var modalSuccess = document.getElementById("modalSuccess");
                modalSuccess.style.display = "block";
              })
              .catch(function(error) {
                modal.style.display = "none";
                alert('could not upload data: ' + error);
              });

    }
}
