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
  th.innerHTML = "Change Status"
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
  updates['/projects/' + projectId + '/status/'] = newStatus;
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
    console.log("new status: inactive")
    updateStatus(this.id, "inactive")
    document.getElementById("deactivated-project-message").classList.add('show')
    document.getElementById("deactivated-project-name").innerHTML = this.id

  } else if (this.classList.contains("status-inactive")) {
    console.log("current status: inactive")
    console.log("new status: active")
    updateStatus(this.id, "active")
    document.getElementById("activated-project-message").classList.add('show')
    document.getElementById("activated-project-name").innerHTML = this.id
  }
  updateTableView()
}


getProjects("active")
getProjects("inactive")
