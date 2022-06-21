// Clear input values when modal is to be shown
$("#add-usergroup-modal").on('show.bs.modal', function() {
  $('#usergroup-name').val('');
  $('#usergroup-description').val('');
});

// Shows loading message in the modal and disables the inputs
function showUserGroupLoading() {
  $('#add-usergroup-modal-loading-message-container').removeClass('hidden');
  $('#usergroup-name').attr('disabled', true);
  $('#usergroup-description').attr('disabled', true);
}

// Hides loading message in the modal and enables the inputs
function hideUserGroupLoading() {
  $('#usergroup-name').attr('disabled', false);
  $('#usergroup-description').attr('disabled', false);
  $('#add-usergroup-modal-loading-message-container').addClass('hidden');
}

// Encodes the given string to the firebase key compatible string
function encodeStringToKey(string) {
  return encodeURIComponent(string).replace(/\./g, '%2E');
}

// Gets triggered when user hits submit button in add usergroup modal
function submitNewUserGroup() {
  const nameInput = $('#usergroup-name');
  const name = (nameInput.val() || '').trim();
  const descriptionInput = $('#usergroup-description');
  const description = (descriptionInput.val() || '').trim();

  if (name && name.length > 30) {
    hideUserGroupLoading();
    alert('User group name is required and should be less than 30 characters');
  } else if (description && description.length > 100) {
    hideUserGroupLoading();
    alert('User group description is should be less than 100 characters');
  } else {
    showUserGroupLoading();

    var key;
    try {
      key = encodeStringToKey(name);
    } catch {
      // This should never occur
      alert('Failed to encode name into a key, please make sure that the user group name does not contain any invalid characters.');
    }

    if (key) {
      firebase.database().ref('v2/userGroups/' + key).once("value", function(snapshot) {
        if (snapshot.exists()) {
          hideUserGroupLoading();
          alert('A group with this name already exists');
        } else {
          var updates = {};
          updates['/v2/userGroups/' + key] = {
            name,
            description,
          };
          firebase.database().ref().update(updates, function(error) {
            hideUserGroupLoading();

            if (error) {
              alert('Failed to add new user! Please make sure you have an active internet connection and that you have enough permission to perform this action.');
              console.error(error);
            } else {
              alert('Successfully added new user group');
              window.location.reload();
            }
          });
        }
      });
    } else {
      hideUserGroupLoading();
    }
  }
}


// Populates the table to list the user groups
// Gets called once at the begining
function addUserGroupsToTable() {
  var tableRef = $("#user-groups-table").DataTable();
  var rows = [];

  var userGroupsRef = firebase.database().ref("v2/userGroups");
  userGroupsRef.once('value', function(snapshot) {
    if (snapshot.exists()) {
      snapshot.forEach(function(data) {
        row_array = [];
        row_array.push(data.val().name);
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

// Populates the table to list members in a user group
// Gets triggered when getUserGroupMembers button is clicked on user group table
function addUsersForSelectedUserGroupToTable() {
  const userGroup = JSON.parse(this.getAttribute('data-usergroup'));
  const groupId = this.id;

  $('#user-group-members-title').text(`User Group Members: ${userGroup.name}`);
  const tableRef = $("#group-members-table").DataTable();
  tableRef.clear();
  const rows = []

  const usersRef = firebase.database().ref('v2/users');
  Object.keys(userGroup.users).forEach((key) => {
    const userRef = usersRef.child(key);
    userRef.once('value', (snapshot) => {
      if (snapshot.exists()) {
        const user = snapshot.val();
        row_array = []
        row_array.push(snapshot.key)
        row_array.push(user.username)
        row_array.push(user.projectContributionCount || 0)
        row_array.push(user.groupContributionCount || 0)
        row_array.push(user.taskContributionCount || 0)
        rows.push(row_array)
        tableRef.row.add(row_array).draw( false )
      }
    });
  });
}

// Populate table to list user groups
addUserGroupsToTable();

// Attach handler for getUserGroupMembers button click
$("#user-groups-table").on('click', '.get-user-groups-members', addUsersForSelectedUserGroupToTable);
