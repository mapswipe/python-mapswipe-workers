function getProjects(status) {
  var ProjectsRef = firebase.database().ref("v2/projects").orderByChild("status").equalTo(status);

  var tableRef = $("#projectsTable-"+status).DataTable();
  var rows = []
  ProjectsRef.once('value', function(snapshot){
    if(snapshot.exists()){
        snapshot.forEach(function(data){

            row_array = []
            row_array.push(data.key)
            row_array.push(data.val().name)
            row_array.push(data.val().projectType)
            row_array.push(data.val().progress + "%")

            if (data.val().status == "inactive") {
              btn1 = addButton(data.key, data.val().status, "active")
              btn2 = addButton(data.key, data.val().status, "finished")
              row_array.push(btn1.outerHTML + btn2.outerHTML)
            } else if (data.val().status == "active") {
              btn1 = addButton(data.key, data.val().status, "inactive")
              btn2 = addButton(data.key, data.val().status, "finished")
              row_array.push(btn1.outerHTML + btn2.outerHTML)
            } else if (data.val().status == "new") {
              btn = addButton(data.key, data.val().status, "active")
              row_array.push(btn.outerHTML)
            } else if (data.val().status == "finished") {
              btn = addButton(data.key, data.val().status, "inactive")
              row_array.push(btn.outerHTML)
            }

            if (data.val().status == "active"){

                btn = document.createElement('button')
                btn.id = data.key
                btn.classList.add("btn")
                btn.classList.add("btn-warning")
                btn.classList.add("isFeatured")
                btn.classList.add("isFeatured-"+data.val().isFeatured)
                btn.addEventListener("click", changeProjectIsFeatured)

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

    var btns = document.getElementsByClassName('change-status')
    for (let item of btns) {
        item.addEventListener("click", changeProjectStatus)
    }


  });

}

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
  console.log('hello update table view')
  status_array = ["new", "active", "inactive", "finished"]

  for (var i = 0; i < status_array.length; i++) {
    status = status_array[i]

    var tableRef = $("#projectsTable-"+status).DataTable();
    var rows = tableRef
        .rows()
        .remove()
        .draw();
    }

    getProjects("new")
    getProjects("active")
    getProjects("inactive")
    getProjects("finished")
    getProjects("archived")
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
getProjects("archived")
