// This script handles the click event for edit buttons
document.addEventListener('DOMContentLoaded', () => {
const editButtons = document.querySelectorAll('.edit-button');

editButtons.forEach(button => {
    button.addEventListener('click', () => {
    const filePath = button.getAttribute('data-file');

    fetch(`http://localhost:4001/edit?file=${encodeURIComponent(filePath)}`)
        .then(response => {
        if (response.ok) {
            console.log(`File "${filePath}" opened for editing.`);
        } else {
            alert(`Failed to open file "${filePath}".`);
        }
        })
        .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while trying to open the file: ' + error.message);
        });
    });
});
});