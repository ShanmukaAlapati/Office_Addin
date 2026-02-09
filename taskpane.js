async function saveNote() {
    const text = document.getElementById("noteText").value;
    const statusDiv = document.getElementById("status");

    if (!text.trim()) {
        statusDiv.textContent = "Please enter some text!";
        statusDiv.style.color = "red";
        return;
    }

    try {
        // Get user's email from Outlook context
        const userEmail = Office.context.mailbox?.userProfile?.emailAddress || 'anonymous';

        const response = await fetch('https://office-addin-54vx.onrender.com/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: text,
                userEmail: userEmail
            })
        });

        const result = await response.json();

        if (result.status === 'saved') {
            statusDiv.textContent = "✓ Saved successfully!";
            statusDiv.style.color = "green";
            document.getElementById("noteText").value = '';
        }
    } catch (error) {
        statusDiv.textContent = "Error: " + error.message;
        statusDiv.style.color = "red";
        console.error(error);
    }
}
