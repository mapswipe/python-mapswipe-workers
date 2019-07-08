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
  document.getElementById("signed-in").style.display = "none";
  document.getElementById("not-signed-in").style.display = "block";
  ui.reset();
  ui.start('#firebaseui-auth-container', uiConfig)

});

// Track the UID of the current user.
var currentUid = null;
firebase.auth().onAuthStateChanged(function(user) {
   // onAuthStateChanged listener triggers every time the user ID token changes.
   // This could happen when a new user signs in or signs out.
   // It could also happen when the current user ID token expires and is refreshed.
   if (user && user.uid != currentUid) {
    // Update the UI when a new user signs in.
    // Otherwise ignore if this is a token refresh.
  // Update the current user UID.
  currentUid = user.uid;
  //document.body.innerHTML = '<h1> Congrats ' + user.displayName + ', you are done! </h1> <h2> Now get back to what you love building. </h2> <h2> Need to verify your email address or reset your password? Firebase can handle all of that for you using the email you provided: ' + user.email + '. <h/2>';
  document.getElementById("not-signed-in").style.display = "none";
  document.getElementById("signed-in").style.display = "block";
  document.getElementById("welcome-name").innerHTML = user.displayName;

  console.log("user signed in")
 } else {
  // Sign out operation. Reset the current user UID.
  currentUid = null;
  console.log("no user signed in");
 }
});
