function getProjects(status) {
  var ProjectsRef = firebase.database().ref("v2/projects").orderByChild("status").equalTo(status);
  var table = document.createElement('table')
  table.classList.add("table")
  var tbody = document.createElement('tbody');

  tr = document.createElement('tr')
  th = document.createElement('th')
  th.innerHTML = "Project ID"
  tr.appendChild(th)

  th = document.createElement('th')
  th.innerHTML = "Name"
  tr.appendChild(th)

  th = document.createElement('th')
  th.innerHTML = "Project Type"
  tr.appendChild(th)

  th = document.createElement('th')
  th.innerHTML = "Progress"
  tr.appendChild(th)

  th = document.createElement('th')
  th.innerHTML = "Status"
  tr.appendChild(th)

  th = document.createElement('th')
  th.innerHTML = "IsFeatured"
  tr.appendChild(th)

  th = document.createElement('th')
  th.innerHTML = "Change Status"
  tr.appendChild(th)

  th = document.createElement('th')
  th.innerHTML = "Change isFeatured"
  tr.appendChild(th)

  tr.appendChild(th)
  tbody.appendChild(tr)

  ProjectsRef.once('value', function(snapshot){
    if(snapshot.exists()){
        snapshot.forEach(function(data){
            tr = document.createElement('tr')

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
            btn = document.createElement('button')
            btn.id = data.key
            btn.classList.add("btn")
            btn.classList.add("btn-warning")
            btn.classList.add("status-"+data.val().status)
            btn.addEventListener("click", changeProjectStatus)

            if (data.val().status == "inactive") {
              btn.innerHTML = "Activate"
            } else if (data.val().status == "active") {
              btn.innerHTML = "Deactivate"
            }
            td.appendChild(btn)
            tr.appendChild(td)

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

            tbody.appendChild(tr)

        });
    }
  });
  table.appendChild(tbody)
  document.getElementById(status + "-projects").appendChild(table)
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
  var inactiveProjects = document.getElementById("inactive-projects")
  while (inactiveProjects.firstChild) {
    inactiveProjects.removeChild(inactiveProjects.firstChild);
  }

  var activeProjects = document.getElementById("active-projects")
  while (activeProjects.firstChild) {
    activeProjects.removeChild(activeProjects.firstChild);
  }

  getProjects("active")
  getProjects("inactive")
}


function changeProjectStatus() {
  console.log('project selected: ' + this.id)

  if (this.classList.contains("status-active")){
    console.log("current status: active")
    updateStatus(this.id, "inactive")
    console.log("new status: inactive")
  } else if (this.classList.contains("status-inactive")) {
    console.log("current status: inactive")
    updateStatus(this.id, "active")
    console.log("new status: active")
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


getProjects("active")
getProjects("inactive")
