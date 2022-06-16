$("#add-usergroup-modal").on('show.bs.modal', function() {
  $('#usergroup-name').val('');
  $('#usergroup-description').val('');
})

function submitNewUserGroup() {
  var nameInput = $('#usergroup-name');
  var name = (nameInput.val() || '').trim();
  var descriptionInput = $('#usergroup-description');
  var description = (descriptionInput.val() || '').trim();

  if (name && name.length <= 50) {
    $('#add-usergroup-modal-loading-message-container').removeClass('hidden');
    nameInput.attr('disabled', true);
    descriptionInput.attr('disabled', true);

    firebase.database().ref('v2/userGroups/' + name).once("value", function(snapshot) {
      if (snapshot.exists()) {
        $('#add-usergroup-modal-loading-message-container').addClass('hidden');
        nameInput.attr('disabled', false);
        descriptionInput.attr('disabled', false);
        alert('A group with this name already exists');
      } else {
        var updates = {};
        updates['/v2/userGroups/' + name] = {
          userGroupName: name,
          description,
        };
        firebase.database().ref().update(updates, function(error) {
          $('#add-usergroup-modal-loading-message-container').addClass('hidden');
          nameInput.attr('disabled', false);
          descriptionInput.attr('disabled', false);

          if (error) {
            alert('Failed to add new user');
            console.info(error);
          } else {
            alert('Successfully added new user group');
            window.location.reload();
          }
        });
      }
    });
  } else {
    nameInput.attr('disabled', false);
    descriptionInput.attr('disabled', false);
    $('#add-usergroup-modal-loading-message-container').addClass('hidden');
    alert('User group name is required and should be less than 50 characters');
  }
}


function addUserGroupsToTable() {
  var tableRef = $("#userGroupsTable").DataTable();
  var rows = [];

  var userGroupsRef = firebase.database().ref("v2/userGroups");
  userGroupsRef.once('value', function(snapshot) {
    if (snapshot.exists()) {
      snapshot.forEach(function(data) {
        row_array = [];
        row_array.push(data.val().userGroupName);
        row_array.push(data.val().description);
        var usersLength = Object.keys(data.val().users || {}).length;

        if (usersLength > 0) {
          // add button for user group members
          btn = document.createElement('button');
          btn.id = data.key;
          btn.setAttribute('data-usergroup', JSON.stringify(data.val()));
          btn.classList.add("btn");
          btn.classList.add("btn-warning");
          btn.classList.add("get-user-groups-members");
          btn.innerHTML = 'getUserGroupMembers()';
          row_array.push(btn.outerHTML);
        } else {
          row_array.push('No members yet');
        }
        rows.push(row_array);
        tableRef.row.add(row_array).draw(false);
      })
    }
  })
}

function addUsersForSelectedUserGroupToTable() {
  const userGroup = JSON.parse(this.getAttribute('data-usergroup'));
  var groupId = this.id;
  var usersLength = Object.keys(userGroup.users || {}).length;

  var tableRef = $("#groupMembersTable").DataTable();
  // remove all existing rows
  tableRef.clear();
  var rows = []

  var ref = firebase.database().ref("v2/users").orderByChild(`userGroups/${userGroup.userGroupName}`).limitToLast(usersLength);
  ref.once('value', function(snapshot){
    if(snapshot.exists()){
      snapshot.forEach(function(data){
        const user = data.val();
        row_array = []
        row_array.push(data.key)
        row_array.push(user.username)
        row_array.push(user.projectContributionCount || 0)
        row_array.push(user.groupContributionCount || 0)
        row_array.push(user.taskContributionCount || 0)
        rows.push(row_array)
        tableRef.row.add(row_array).draw( false )
      })
    }
  })
}

addUserGroupsToTable();
$("#userGroupsTable").on('click', '.get-user-groups-members', addUsersForSelectedUserGroupToTable);
