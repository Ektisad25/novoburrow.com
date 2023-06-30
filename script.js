// Signup form submission
document.getElementById("signup-form").addEventListener("submit", function(event) {
    event.preventDefault();
    var username = document.getElementById("signup-username").value;
    var password = document.getElementById("signup-password").value;
  
    // Perform signup validation and processing here
    // You can use AJAX to send the signup data to the server
  
    // Display success or error message
    var signupMessage = document.getElementById("signup-message");
    signupMessage.textContent = "Signup successful!";
  
    // Clear the form fields
    document.getElementById("signup-username").value = "";
    document.getElementById("signup-password").value = "";
  });
  
  var users = [
    { username: "admin", password: "password" },
    { username: "user1", password: "123456" },
    { username: "user2", password: "qwerty" }
  ];
  
  // Login form submission
  document.getElementById("login-form").addEventListener("submit", function(event) {
    event.preventDefault();
    var username = document.getElementById("login-username").value;
    var password = document.getElementById("login-password").value;
  
    // Search for the user in the users array
    var user = users.find(function(user) {
      return user.username === username && user.password === password;
    });
  
    // Display success or error message
    var loginMessage = document.getElementById("login-message");
    if (user) {
      loginMessage.textContent = "Login successful!";
    } else {
      loginMessage.textContent = "Invalid username or password.";
    }
  
    // Clear the form fields
    document.getElementById("login-username").value = "";
    document.getElementById("login-password").value = "";
  });