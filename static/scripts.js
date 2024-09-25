// Event listener for the file input to display the selected file name
document.getElementById('resume').addEventListener('change', function() {
    var fileInput = document.getElementById('resume');
    if (fileInput.files.length > 0) {
        var fileName = fileInput.files[0].name;
        document.getElementById('file-name').textContent = "Selected file: " + fileName;
    } else {
        document.getElementById('file-name').textContent = "";
    }
});

// Event listener for form submission
document.getElementById('cv-upload-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent default form submission

    var formData = new FormData(this); // Create a FormData object

    // Send the form data using fetch API
    fetch('/process-uploaded_cv', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.botResponse); });
        }
        return response.json(); // Parse JSON response
    })
    .then(data => {
        // Handle success
        console.log(data);
        alert("CV uploaded successfully!");
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
        alert("Error uploading CV: " + error.message);
    });
});

// Event listener for ranking applicants button
document.getElementById('rank-applicants-btn').addEventListener('click', function() {
    var jobDescription = document.querySelector('textarea[name="job_description"]').value;

    fetch('/rank-applicants', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({ job_description: jobDescription })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error in ranking applicants');
        }
        return response.json(); // Parse JSON response
    })
    .then(data => {
        // Handle success and display ranking results
        console.log(data);
        document.getElementById('ranking-results').innerText = JSON.stringify(data.response, null, 2);
        alert("Ranking completed successfully!");
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
        alert("Error ranking applicants: " + error.message);
    });
});