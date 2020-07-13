function addEventListeners(status) {
  $("#projectsTable-"+status).on('click', '.change-status', changeProjectStatus);
  $("#projectsTable-"+status).on('click', '.change-isFeatured', changeProjectIsFeatured);
}

/* Download teams from firebase. This is needed to display
the teamName instead of just the teamId for projects. */
function getTeams() {
    var teams = {}
    var TeamsRef = firebase.database().ref("v2/teams");
    TeamsRef.once('value', function(snapshot){
        if(snapshot.exists()){
            snapshot.forEach(function(data){
                teams[data.key] = {
                    "teamName": data.val().teamName
                    }
                })
            }
        })
    console.log("got teams from firebase")
    return teams
}

/* Download projects from firebase and add each project as a row in the table.
There 4 tables, referring to the status of a project.
active and private_active projects are diplayed in the same table. */
function getProjects(status) {
  // init basic structure and get data table html element
  switch (status) {
    case "active":
    case "private_active":
         var tableRef = $("#projectsTable-active").DataTable();
         break;
    case "inactive":
    case "private_inactive":
         var tableRef = $("#projectsTable-inactive").DataTable();
         break;
    case "finished":
    case "private_finished":
         var tableRef = $("#projectsTable-finished").DataTable();
         break;
    case "archived":
         var tableRef = $("#projectsTable-archived").DataTable();
         break;
  }

  var rows = []

  console.log('start download projects from firebase')
  var teams = getTeams()
  var projects =  []
  var ProjectsRef = firebase.database().ref("v2/projects").orderByChild("status").equalTo(status);
  ProjectsRef.once('value', function(snapshot){
    if(snapshot.exists()){
        snapshot.forEach(function(data){
            info = {
                    "projectId": data.key,
                    "name": data.val().name || "undefined",
                    "projectType": data.val().projectType || 1,
                    "progress": data.val().progress || 0
                    }

            // set visibility based on status
            switch (status) {
                case "active":
                case "inactive":
                case "finished":
                case "archived":
                    info["visibility"] = "public";
                    break;
                case "private_active":
                case "private_inactive":
                case "private_finished":
                case "private_archived":
                    // get the teamName from teams instead of displaying the teamId
                    info["visibility"] = teams[data.val().teamId]["teamName"];
                    break;
            }

            row_array = []
            row_array.push(info["projectId"])
            row_array.push(info["name"])  // set project name
            row_array.push(info["visibility"])  // set visibility
            row_array.push(info["projectType"])  // set project type
            row_array.push(info["progress"] + "%")  // set project progress

            // set extra columns based on status
            switch (status) {
                case "active":
                    btn1 = addButton(data.key, data.val().status, "inactive")
                    btn2 = addButton(data.key, data.val().status, "finished")
                    row_array.push(btn1.outerHTML + btn2.outerHTML)
                    btn = addButtonChangeIsFeatured(data.key, data.val().isFeatured)
                    if (data.val().isFeatured) {
                      row_array.push("<b>true</b><br>" + btn.outerHTML)
                    } else {
                      row_array.push("false<br>" + btn.outerHTML)
                    }
                    break;
                case "private_active":
                    btn1 = addButton(data.key, data.val().status, "private_inactive")
                    btn2 = addButton(data.key, data.val().status, "private_finished")
                    row_array.push(btn1.outerHTML + btn2.outerHTML)

                    btn = addButtonChangeIsFeatured(data.key, data.val().isFeatured)
                    if (data.val().isFeatured) {
                      row_array.push("<b>true</b><br>" + btn.outerHTML)
                    } else {
                      row_array.push("false<br>" + btn.outerHTML)
                    }
                    break;
                case "inactive":
                    btn1 = addButton(data.key, data.val().status, "active")
                    btn2 = addButton(data.key, data.val().status, "finished")
                    row_array.push(btn1.outerHTML + btn2.outerHTML)
                    break;
                case "private_inactive":
                    btn1 = addButton(data.key, data.val().status, "private_active")
                    btn2 = addButton(data.key, data.val().status, "private_finished")
                    row_array.push(btn1.outerHTML + btn2.outerHTML)
                    break;
                case "finished":
                    btn = addButton(data.key, data.val().status, "inactive")
                    row_array.push(btn.outerHTML)
                    break
                case "private_finished":
                    btn = addButton(data.key, data.val().status, "private_inactive")
                    row_array.push(btn.outerHTML)
                    break;
            }

            rows.push(row_array)
            tableRef.row.add(row_array).draw( false )
        })
    }
  })
  $('.dataTables_length').addClass('bs-select');
  console.log('added data table styles')

}

/* add a button in the data table with specific class
to indicate the desired new status. This class will be used by
the changeProjectStatus() function to set the right status in Firebase
when clicking on the button. */
function addButton(id, oldStatus, newStatus){
  btn = document.createElement('button')
  btn.id = id
  btn.classList.add("btn")
  btn.classList.add("btn-warning")
  btn.classList.add("change-status")
  btn.classList.add("new-status-"+newStatus)
  btn.innerHTML = "set to '"+newStatus+"'"

  return btn
}

/* add a button to change the isFeatured attribute of a project.
This btn has a class which indicates the current isFeatured status.
This will be used by updateIsFeatured() function to set new attribute
in Firebase. */
function addButtonChangeIsFeatured(id, currentValue) {
    btn = document.createElement('button')
    btn.id = id
    btn.classList.add("btn")
    btn.classList.add("btn-warning")
    btn.classList.add("change-isFeatured")
    btn.classList.add("isFeatured-"+currentValue)
    if (currentValue) {
      btn.innerHTML = 'set to "false"'
    } else {
      btn.innerHTML = 'set to "true"'
    }

    return btn
}

/* Set the new status in Firebase for a project */
function updateStatus(projectId, newStatus) {
  var updates = {};
  updates['/v2/projects/' + projectId + '/status/'] = newStatus;
  return firebase.database().ref().update(updates);

}

/* Set the new isFeatured attribute in Firebase for a project */
function updateIsFeatured(projectId, newStatus) {
  // Write the new post's data simultaneously in the posts list and the user's post list.
  var updates = {};
  updates['/v2/projects/' + projectId + '/isFeatured/'] = newStatus;
  return firebase.database().ref().update(updates);

}

/* this function updates all tables. It reloads all data from firebase and
sets the rows in the data table. */
function updateTableView() {
    status_array = [
        "active",
        "private_active",
        "inactive",
        "private_inactive",
        "finished",
        "private_finished",
        "archived"
    ]

  for (var i = 0; i < status_array.length; i++) {
    status = status_array[i]

    var tableRef = $("#projectsTable-"+status).DataTable();
    var rows = tableRef
        .rows()
        .remove()
        .draw();
    getProjects(status)
    }

  console.log('updated table view')
}

/* This is triggered when users click on a button
to change the status of a project in firebase.
It looks for the class of the button and sets the new status
accordingly using the updateStatus function.
*/
function changeProjectStatus() {
  console.log('project selected: ' + this.id)


  if (this.classList.contains("new-status-active")){
    updateStatus(this.id, "active")
    console.log("new status: active")
  } else if (this.classList.contains("new-status-inactive")) {
    updateStatus(this.id, "inactive")
    console.log("new status: inactive")
  } else if (this.classList.contains("new-status-finished")) {
    updateStatus(this.id, "finished")
    console.log("new status: finished")
  } else if (this.classList.contains("new-status-private_active")) {
    updateStatus(this.id, "private_active")
    console.log("new status: private_active")
  } else if (this.classList.contains("new-status-private_inactive")) {
    updateStatus(this.id, "private_inactive")
    console.log("new status: private_inactive")
  } else if (this.classList.contains("new-status-private_finished")) {
    updateStatus(this.id, "private_finished")
    console.log("new status: private_finished")
  }
  // after updating the status we reload all tables
  updateTableView()
}

/* This is triggered when users click on a button
to change if a project is features in the app.
It looks for the class of the button (which tells the current isFeatured value)
and sets the new featured status accordingly using the updateIsFeatured function.
*/
function changeProjectIsFeatured() {
  console.log('project selected: ' + this.id)

  if (this.classList.contains("isFeatured-true")){
    console.log("current status: featured")
    updateIsFeatured(this.id, false)
    console.log("new status: not featured")
  } else if (this.classList.contains("isFeatured-false")) {
    console.log("current status: not featured")
    updateIsFeatured(this.id, true)
    console.log("new status: featured")
  }
  // after updating the isFeatured attribute we reload all tables
  updateTableView()
}

/* Load the data and populate table */
status_array = [
    "active",
    "private_active",
    "inactive",
    "private_inactive",
    "finished",
    "private_finished",
    "archived"
]
for (var i = 0; i < status_array.length; i++) {
    status = status_array[i]
    getProjects(status)
    addEventListeners(status)
}
