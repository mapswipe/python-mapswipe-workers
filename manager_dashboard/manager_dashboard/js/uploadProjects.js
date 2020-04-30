var database = firebase.database();

function upload_project_image() {
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
    }, function() {
      // Handle successful uploads on complete
      // For instance, get the download URL: https://firebasestorage.googleapis.com/...
      uploadImage.snapshot.ref.getDownloadURL().then(function(downloadURL) {
        console.log('File available at', downloadURL);
        return downloadURL
      });
    });

}


function submitInfo() {

    if (currentUid == null) {
      alert("You are not logged in.");
    } else {

    // get basic project information
    var projectTopic = document.getElementById("projectTopic").value;
    var projectRegion = document.getElementById("projectRegion").value;
    var projectNumber = document.getElementById("projectNumber").value;
    var requestingOrganisation = document.getElementById("requestingOrganisation").value;
    var name = projectTopic + ' - ' + projectRegion + ' (' + projectNumber + ')\n' + requestingOrganisation


    var lookFor = document.getElementById("lookFor").value;
    var projectDetails = document.getElementById("projectDetails").value;
    var projectType = document.getElementById("projectType").value;

    var verificationNumber = document.getElementById("verificationNumber").value;
    var createdBy = currentUid;
    var groupSize = document.getElementById("groupSize").value;

    if (projectType == 1) {

        var zoomLevel = document.getElementById("zoomLevel").value;
        var geometry = BuildAreaGeometry;
        var tileServer = {
          name: document.getElementById("tileServerBuildArea").value,
          url: document.getElementById("tileServerUrlBuildArea").value,
          wmtsLayerName: document.getElementById("tileServerLayerNameBuildArea").value,
          credits: document.getElementById("tileServerCreditsBuildArea").value
        };

        var mapswipe_import = {
            name: name,
            projectRegion: projectRegion,
            projectTopic: projectTopic,
            projectNumber: projectNumber,
            requestingOrganisation: requestingOrganisation,
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
      var geometry = ChangeDetectionGeometry;
      var tileServerA = {
        name: document.getElementById("tileServerChangeDetectionA").value,
        url: document.getElementById("tileServerUrlChangeDetectionA").value,
        wmtsLayerName: document.getElementById("tileServerLayerNameChangeDetectionA").value,
        caption: document.getElementById("captionChangeDetectionA").value,
        date: document.getElementById("dateChangeDetectionA").value,
        credits: document.getElementById("tileServerCreditsChangeDetectionA").value
      };
      var tileServerB = {
        name: document.getElementById("tileServerChangeDetectionB").value,
        url: document.getElementById("tileServerUrlChangeDetectionB").value,
        wmtsLayerName: document.getElementById("tileServerLayerNameChangeDetectionB").value,
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
        console.log(mapswipe_import)

        // upload projectDraft to firebase once image has been uploaded

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
}
