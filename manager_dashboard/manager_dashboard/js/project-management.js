function addEventListeners(status) {
  $("#projectsTable-"+status).on('click', '.change-status', changeProjectStatus);
  $("#projectsTable-"+status).on('click', '.change-isFeatured', changeProjectIsFeatured);
}

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


function getProjects(status) {
  console.log('start download projects from firebase')
  var teams = getTeams()
  var projects =  []
  var ProjectsRef = firebase.database().ref("v2/projects").orderByChild("status").equalTo(status);
  ProjectsRef.once('value', function(snapshot){
    if(snapshot.exists()){
        snapshot.forEach(function(data){
            info = {
                    "projectId": data.key,
                    "name": data.val().name,
                    "projectType": data.val().projectType,
                    "progress": data.val().progress
                    }

            // set visibility based on status
            switch (status) {
                case "active":
                case "inactive":
                case "finished":
                    info["visibility"] = "public";
                    break;
                case "private_active":
                case "private_inactive":
                case "private_finished":
                    info["visibility"] = teams[data.val().teamId]["teamName"];
                    break;
            }
            projects.push(info)
        })
    }
  })

  return projects
}


function addProjectToTable(status){
    // init basic structure
    var tableRef = $("#projectsTable-"+status).DataTable();
    var rows = []

    // get projects based on status
    switch (status) {
        case "active":
            // get active and private_active projects
            public_projects = getProjects("active")
            private_projects = getProjects("private_active")
            merged_projects = {public_projects, private_projects};
            break;
        case "inactive":
            // get inactive and private inactive projects
            public_projects = getProjects("inactive")
            private_projects = getProjects("private_inactive")
            break;
        case "finished":
            // get finished and private finished projects
            public_projects = getProjects("finished")
            private_projects = getProjects("private_finished")
            merged_projects = {public_projects, private_projects};
            break;
        case "archived":
            // for archived projects we do not distinguish public or private
            public_projects = getProjects("archived")
            private_projects = {}
            break;
    }

    console.log(public_projects)
    console.log(public_projects.length)

    for (var i = 0; i < public_projects.length; i++) {
        console.log(public_projects[i]);
        //Do something
        console.log('hey')
    }




}


    /*


    $('.dataTables_length').addClass('bs-select');
    console.log('added data table styles')


            /*
                })
            projectId = data.key
            var projectStatus = data.val().status

            row_array = []
            row_array.push(projectId)
            row_array.push(data.val().name)  // set project name
            row_array.push("Public")  // set visibility
            row_array.push(data.val().projectType)  // set project type
            row_array.push(data.val().progress + "%")  // set project progress

            // set visibility based on status
            switch (projectStatus) {
                case "active":
                case "inactive":
                case "finished":
                    visibility = "public";
                    console.log("public");
                    break;
                case "private_active":
                case "private_inactive":
                case "private_finished":
                    console.log(teams)
                    //console.log(data.val().teamId)
                    //console.log(data.val())
                    //visibility = teams[data.val().teamId]["teamName"]
            }

            if (data.val().status == "inactive") {
              btn1 = addButton(data.key, data.val().status, "active")
              btn2 = addButton(data.key, data.val().status, "finished")
              row_array.push(btn1.outerHTML + btn2.outerHTML)
            } else if (data.val().status == "active") {
              btn1 = addButton(data.key, data.val().status, "inactive")
              btn2 = addButton(data.key, data.val().status, "finished")
              row_array.push(btn1.outerHTML + btn2.outerHTML)
            } else if (data.val().status == "finished") {
              btn = addButton(data.key, data.val().status, "inactive")
              row_array.push(btn.outerHTML)
            }

            if (data.val().status == "active"){

                btn = document.createElement('button')
                btn.id = data.key
                btn.classList.add("btn")
                btn.classList.add("btn-warning")
                btn.classList.add("change-isFeatured")
                btn.classList.add("isFeatured-"+data.val().isFeatured)

                if (data.val().isFeatured === true) {
                  btn.innerHTML = 'set to "false"'
                  row_val = "<b>"+data.val().isFeatured+"</b>"
                  row_array.push(row_val + "<br>" + btn.outerHTML)
                } else if (data.val().isFeatured === false) {
                  btn.innerHTML = 'set to "true"'
                  row_val = data.val().isFeatured
                  row_array.push(row_val + "<br>" + btn.outerHTML)
                }

                row_array.push(row_val + btn.outerHTML)
            }



            rows.push(row_array)
            tableRef.row.add(row_array).draw( false )
        });
    };
    $('.dataTables_length').addClass('bs-select');
    console.log('added data table styles')
  });
  */


/*
function addProjectToTable(status):
    var tableRef = $("#projectsTable-"+status).DataTable();
    var rows = []


    $('.dataTables_length').addClass('bs-select');
    console.log('added data table styles')

*/

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

function updateStatus(projectId, newStatus) {
  // Write the new post's data simultaneously in the posts list and the user's post list.
  var updates = {};
  updates['/v2/projects/' + projectId + '/status/'] = newStatus;
  return firebase.database().ref().update(updates);

}

function updateIsFeatured(projectId, newStatus) {
  // Write the new post's data simultaneously in the posts list and the user's post list.
  var updates = {};
  updates['/v2/projects/' + projectId + '/isFeatured/'] = newStatus;
  return firebase.database().ref().update(updates);

}

function updateTableView() {
  status_array = ["active", "inactive", "finished", "archived"]

  for (var i = 0; i < status_array.length; i++) {
    status = status_array[i]

    var tableRef = $("#projectsTable-"+status).DataTable();
    var rows = tableRef
        .rows()
        .remove()
        .draw();
    }

    getProjects("active")
    getProjects("inactive")
    getProjects("finished")
    getProjects("archived")

  console.log('updated table view')
}


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
  }
  updateTableView()
}

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
  updateTableView()
}


status_array = ["active", "inactive", "finished", "archived"]
status_array = ["inactive"]

  for (var i = 0; i < status_array.length; i++) {
    status = status_array[i]

    addProjectToTable(status)
    //getProjects(status)
    addEventListeners(status)
  }
