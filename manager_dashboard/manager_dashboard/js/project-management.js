function getProjects(status) {
  var ProjectsRef = firebase.database().ref("v2/projects").orderByChild("status").equalTo(status);

  var tableRef = document.getElementById('projectsTable-'+status).getElementsByTagName('tbody')[0];

  ProjectsRef.once('value', function(snapshot){
    if(snapshot.exists()){
        snapshot.forEach(function(data){

            tr = tableRef.insertRow();
            td = document.createElement('td')
            td.innerHTML = data.key
            tr.appendChild(td)

            td = document.createElement('td')
            td.innerHTML = data.val().name
            tr.appendChild(td)

            td = document.createElement('td')
            td.innerHTML = data.val().projectType
            tr.appendChild(td)

            td = document.createElement('td')
            td.innerHTML = data.val().progress + "%"
            tr.appendChild(td)

            td = document.createElement('td')
            td.innerHTML = data.val().status
            tr.appendChild(td)

            td = document.createElement('td')
            if (data.val().isFeatured === true) {
              td.innerHTML = "<b>"+data.val().isFeatured+"</b>"
            } else if (data.val().isFeatured === false) {
              td.innerHTML = data.val().isFeatured
            }
            tr.appendChild(td)


            td = document.createElement('td')

            if (data.val().status == "inactive") {
              btn = addButton(data.key, data.val().status, "active")
              td.appendChild(btn)
              btn = addButton(data.key, data.val().status, "finished")
              td.appendChild(btn)
            } else if (data.val().status == "active") {
              btn = addButton(data.key, data.val().status, "inactive")
              td.appendChild(btn)
              btn = addButton(data.key, data.val().status, "finished")
              td.appendChild(btn)
            } else if (data.val().status == "new") {
              btn = addButton(data.key, data.val().status, "active")
              td.appendChild(btn)
            } else if (data.val().status == "finished") {
              btn = addButton(data.key, data.val().status, "inactive")
              td.appendChild(btn)
            }
            tr.appendChild(td)

            if (data.val().status == "active"){
                td = document.createElement('td')
                btn = document.createElement('button')
                btn.id = data.key
                btn.classList.add("btn")
                btn.classList.add("btn-warning")
                btn.classList.add("isFeatured-"+data.val().isFeatured)
                btn.addEventListener("click", changeProjectIsFeatured)

                if (data.val().isFeatured === true) {
                  btn.innerHTML = 'set to "false"'
                } else if (data.val().isFeatured === false) {
                  btn.innerHTML = 'set to "true"'
                }
                td.appendChild(btn)
                tr.appendChild(td)
            }
        });
    };
    $("#projectsTable-"+status).DataTable();
    $('.dataTables_length').addClass('bs-select');
  });

}

function addButton(id, oldStatus, newStatus){
  btn = document.createElement('button')
  btn.id = id
  btn.classList.add("btn")
  btn.classList.add("btn-warning")
  btn.classList.add("new-status-"+newStatus)
  btn.addEventListener("click", changeProjectStatus)
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
  var newProjects = document.getElementById("projectsTable-new").getElementsByTagName('tbody')[0]
  while (newProjects.firstChild) {
    newProjects.removeChild(newProjects.firstChild);
  }

  var inactiveProjects = document.getElementById("projectsTable-inactive").getElementsByTagName('tbody')[0]
  while (inactiveProjects.firstChild) {
    inactiveProjects.removeChild(inactiveProjects.firstChild);
  }

  var activeProjects = document.getElementById("projectsTable-active").getElementsByTagName('tbody')[0]
  while (activeProjects.firstChild) {
    activeProjects.removeChild(activeProjects.firstChild);
  }

  var finishedProjects = document.getElementById("projectsTable-finished").getElementsByTagName('tbody')[0]
  while (finishedProjects.firstChild) {
    finishedProjects.removeChild(finishedProjects.firstChild);
  }

  getProjects("new")
  getProjects("active")
  getProjects("inactive")
  getProjects("finished")
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


getProjects("new")
getProjects("active")
getProjects("inactive")
getProjects("finished")
