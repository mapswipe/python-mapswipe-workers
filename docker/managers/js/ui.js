var uiConfig = {
  signInOptions: [
    // Specify providers you want to offer your users.
    firebase.auth.EmailAuthProvider.PROVIDER_ID
  ],
  credentialHelper: firebaseui.auth.CredentialHelper.NONE,
  // Terms of service url can be specified and will show up in the widget.
  tosUrl: '<your-tos-url>'
};
// Initialize the FirebaseUI Widget using Firebase.
var ui = new firebaseui.auth.AuthUI(firebase.auth());
// The start method will wait until the DOM is loaded.
ui.start('#firebaseui-auth-container', uiConfig);

document.getElementById('sign-out').addEventListener('click', function() {
  firebase.auth().signOut();
  document.getElementById("signed-in-manager").style.display = "none";
  document.getElementById("not-signed-in").style.display = "block";
  document.getElementById("log-out-message").classList.add('show')
  ui.reset();
  ui.start('#firebaseui-auth-container', uiConfig)

});

// Track the UID of the current user.
var currentUid = null;

let callback = null;
let metadataRef = null;

firebase.auth().onAuthStateChanged(function(user) {
   // onAuthStateChanged listener triggers every time the user ID token changes.
   // This could happen when a new user signs in or signs out.
   // It could also happen when the current user ID token expires and is refreshed.
   if (user && user.uid != currentUid) {
    // Update the UI when a new user signs in.
    // Otherwise ignore if this is a token refresh.
      // Update the current user UID.
      console.log(user.displayName)
      currentUid = user.uid;

      document.getElementById("not-signed-in").style.display = "none";

    firebase.auth().currentUser.getIdTokenResult()
      .then((idTokenResult) => {
         // Confirm the user is an Admin.
         if (!!idTokenResult.claims.projectManager) {
           // Show admin UI.
           console.log('this user is a project manager')
           document.getElementById("welcome-name-manager").innerHTML = user.displayName;
           document.getElementById("signed-in-manager").style.display = "block";
           document.getElementById("signed-in-manager").style.display = "block";
           document.getElementById("welcome-message-manager").classList.add('show')
         } else {
           // Show regular user UI.
           console.log('this user is not a project manager')
           document.getElementById("welcome-name").innerHTML = user.displayName;
           document.getElementById("welcome-message-no-manager").classList.add('show')
         }
      })
      .catch((error) => {
        console.log(error);
      });



      console.log("user signed in")
 } else {
  // Sign out operation. Reset the current user UID.
  currentUid = null;
  console.log("no user signed in");
 }
});


