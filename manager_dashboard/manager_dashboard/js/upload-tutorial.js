var database = firebase.database();


function getFormInput() {
    var form_data = {
        lookFor: document.getElementById("lookFor").value,
        createdBy: currentUid,
        name: document.getElementById("name").value
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

    return form_data
}

function upload_project_image(id) {

    var file = document.getElementById(id).files[0]
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
        if (id == "image1") {
            exampleImage1 = downloadURL
        } else if (id == "image2") {
            exampleImage2 = downloadURL
        }
      });
    });


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

            upload_project_image("image1")
            upload_project_image("image2")


            // TODO: this should be implemented better...
            setTimeout(function() {

                mapswipe_import.exampleImage1 = exampleImage1
                mapswipe_import.exampleImage2 = exampleImage2

                console.log(mapswipe_import)

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
            }, 15000)
        }
}
