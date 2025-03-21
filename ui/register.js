document.getElementById("register-form").addEventListener("submit", function(event) {
event.preventDefault();

const name = document.getElementById("name").value;
const ageRange = document.getElementById("age-range").value;
const activities = document.getElementById("activities").value.split(",");

fetch("/register_user", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, age_range: ageRange, preferred_activities: activities })
})
.then(response => response.json())
.then(data => {
    if (data.user_id) {
        document.getElementById("success-message").innerText =
            `Registration successful! Your User ID is: ${data.user_id}`;
        document.getElementById("success-message").style.display = "block";
    } else {
        alert("Registration failed. Try again.");
    }
})
.catch(error => console.error("Error:", error));
});