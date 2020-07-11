function addEventListenersTeams() {
  $("#teamsTable").on('click', '.get-team-members', getTeamMembers);
}


function addTeamsToTable() {

    var tableRef = $("#teamsTable").DataTable();
    var rows = []

    var TeamsRef = firebase.database().ref("v2/teams");
    TeamsRef.once('value', function(snapshot){
        if(snapshot.exists()){
            snapshot.forEach(function(data){
                row_array = []
                row_array.push(data.key)
                row_array.push(data.val().teamName)
                row_array.push(data.val().teamToken)
                // add button for team members
                btn = document.createElement('button')
                btn.id = data.key
                btn.classList.add("btn")
                btn.classList.add("btn-warning")
                btn.classList.add("get-team-members")
                btn.innerHTML = 'getTeamMembers()'
                row_array.push(btn.outerHTML)
                rows.push(row_array)
                tableRef.row.add(row_array).draw( false )
                })
            }
        })
    $('.dataTables_length').addClass('bs-select');
    console.log('added data table styles')
    console.log("got teams from firebase")
}


function getTeamMembers() {
    console.log('team selected: ' + this.id)
    var teamId = this.id

    var tableRef = $("#teamMembersTable").DataTable();
    var rows = []

    var TeamsRef = firebase.database().ref("v2/users").orderByChild("teamId").equalTo(teamId);;
    TeamsRef.once('value', function(snapshot){
        if(snapshot.exists()){
            snapshot.forEach(function(data){
                row_array = []
                row_array.push(data.key)
                row_array.push(data.val().username)
                row_array.push(data.val().projectContributionCount)
                row_array.push(data.val().groupContributionCount)
                row_array.push(data.val().taskContributionCount)
                rows.push(row_array)
                tableRef.row.add(row_array).draw( false )
                })
            }
        })
    $('.dataTables_length').addClass('bs-select');
    console.log('added data table styles')
    console.log("got teams from firebase")
}


addTeamsToTable();
addEventListenersTeams()