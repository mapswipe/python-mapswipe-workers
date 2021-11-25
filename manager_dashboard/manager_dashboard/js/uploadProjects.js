var database = firebase.database();


function getFormInput() {
    var form_data = {
        projectRegion: document.getElementById("projectRegion").value,
        projectTopic: document.getElementById("projectTopic").value,
        projectNumber: document.getElementById("projectNumber").value,
        requestingOrganisation: document.getElementById("requestingOrganisation").value,
        lookFor: document.getElementById("lookFor").value,
        projectDetails: document.getElementById("projectDetails").value,
        image: image,
        verificationNumber: parseInt(document.getElementById("verificationNumber").value),
        groupSize: parseInt(document.getElementById("groupSize").value),
        createdBy: currentUid,
        tutorialId: document.getElementById("tutorial").value
    }

    form_data.name = form_data.projectTopic + ' - ' +
        form_data.projectRegion +
        ' (' + form_data.projectNumber + ')\n' +
        form_data.requestingOrganisation

    // add teamId if visibility is not set to public
    visibility = document.getElementById("visibility").value
    if (visibility !== "public") {
        form_data.teamId = visibility
        maxTasksPerUser = document.getElementById("maxTasksPerUser").value
        if (maxTasksPerUser > 0) {
            form_data.maxTasksPerUser = maxTasksPerUser
        }
    }

    // add project type specific attributes
    projectType = document.getElementById("projectType").value
    switch (projectType) {
        case "build_area":
            form_data.projectType = 1;
            form_data.zoomLevel = parseInt(document.getElementById("zoomLevel").value);
            form_data.geometry = JSON.parse(projectAoiGeometry)
            form_data.tileServer = {
              name: document.getElementById("tileServerAName").value,
              url: document.getElementById("tileServerAUrl").value,
              wmtsLayerName: document.getElementById("tileServerALayerName").value,
              credits: document.getElementById("tileServerACredits").value
            };
            break;
        case "footprint":
            form_data.projectType = 2;
            switch($("#geometryInputOption").val()){
                case "link":
                    form_data.inputType = "link"
                    form_data.geometry = $("#inputTaskGeometries").val();
                    break;
                case "aoi_file":
                    form_data.inputType = "aoi_file";
                    form_data.geometry = JSON.parse(projectAoiGeometry);
                    filter_val = $("#inputFilter").val();
                    filter_val != "other" ? form_data.filter = $("#inputFilter").val() : form_data.filter = $("#inputFilterText").val();
                    break;
                case "id":
                    form_data.inputType = "TMId"
                    filter_val = $("#inputFilter").val();
                    filter_val != "other" ? form_data.filter = $("#inputFilter").val() : form_data.filter = $("#inputFilterText").val();
                    form_data.TMId = $("#inputTaskGeometriesId").val();
                    break;
            }
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
            form_data.geometry = JSON.parse(projectAoiGeometry)
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
    return form_data
}


function uploadProjectImage(mapswipe_import) {

    var modal = document.getElementById("uploadModal");
    var modalValidating = document.getElementById("modalValidating");
    modalValidating.style.display = "none";

    modal.style.display = "block";
    var modalOngoing = document.getElementById("modalOngoing");
    modalOngoing.style.display = "block";

    var modal = document.getElementById("uploadModal");
    modal.style.display = "block";

    var file = document.getElementById('image').files[0]
    console.log(file)
    var filename = file.name
    console.log(filename)
    // Create a reference to the image
    var storageRef = firebase.storage().ref();
    var projectImageRef = storageRef.child('projectImages/'+filename);

    var uploadImage = projectImageRef.put(file);
    uploadImage.on('state_changed', function(snapshot){
      // Observe state change events such as progress, pause, and resume
      // Get task progress, including the number of bytes uploaded and the total number of bytes to be uploaded
      var progress = (snapshot.bytesTransferred / snapshot.totalBytes) * 100;
      console.log('Upload is ' + progress + '% done');
      switch (snapshot.state) {
        case firebase.storage.TaskState.PAUSED: // or 'paused'
          console.log('Upload is paused');
          break;
        case firebase.storage.TaskState.RUNNING: // or 'running'
          console.log('Upload is running');
          break;
      }
    }, function(error) {
      // Handle unsuccessful uploads
      modal.style.display = "none";
    }, function() {
      // Handle successful uploads on complete
      // For instance, get the download URL: https://firebasestorage.googleapis.com/...
      uploadImage.snapshot.ref.getDownloadURL().then(function(downloadURL) {
        console.log('File available at', downloadURL);
        mapswipe_import.image = downloadURL

        // TODO: unwrap this here and use separate function and await
        firebase.database().ref('v2/projectDrafts/').push().set(mapswipe_import)
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
      });
    });
}


function checkImageryUrl() {
    // check if url A contains the placeholders when using custom imagery
    urlA = document.getElementById("tileServerAUrl").value
    nameA = document.getElementById("tileServerAName").value
    if (nameA === "custom" & (!urlA.includes("{x}") | !urlA.includes("{y}") | !urlA.includes("{z}"))) {
        alert("The imagery url A must contain {x}, {y} and {z} placeholders.")
        return false
    }

    // check if url B contains the placeholders when using custom imagery
    urlB = document.getElementById("tileServerBUrl").value
    nameB = document.getElementById("tileServerBName").value
    if (nameB === "custom" & (!urlB.includes("{x}") | !urlB.includes("{y}") | !urlB.includes("{z}"))) {
        alert("The imagery url B must contain {x}, {y} and {z} placeholders.")
        return false
    }

    // check passed
    return true
}


function uploadToFirebase() {
    switch (currentUid) {
        case null:
            alert("You are not logged in.");
        default:
            // TODO: add checks if all input values are valid, e.g. image available
            if (checkImageryUrl() === false) {
                console.log("could not create project due to imagery url.")
            }
            else {
                 // get form data
                mapswipe_import = getFormInput()
                // upload projectDraft to firebase once image has been uploaded
                // if inputGeometries is a TMId, check if it is a valid project, only upload if it is
                var modal = document.getElementById("uploadModal");
                modal.style.display = "block";
                var modalValidating = document.getElementById("modalValidating");
                modalValidating.style.display = "block";
                switch(mapswipe_import.inputType){
                    case "link":
                        uploadProjectImage(mapswipe_import)
                        break;
                    case "aoi_file":
                    console.log("here i am rock you liek a hurricane")
                        answer = countObjectsInFilter(mapswipe_import.geometry, mapswipe_import.filter)
                        if (answer.Error != null){
                            alert(`Invalid TMId: ${answer.Error}`)
                        }
                        else {
                            uploadProjectImage(mapswipe_import)
                        }
                        break;
                    case "TMId":
                        validateTMIdAndFilter(mapswipe_import.TMId, mapswipe_import.filter).then(answer=>{
                            if (answer.Error != null){
                                alert(`Invalid: ${answer.Error}`)
                            }
                            else {
                                mapswipe_import.geometry = answer
                                uploadProjectImage(mapswipe_import)
                            }
                        })
                    break;
                }
            }
    }
}
