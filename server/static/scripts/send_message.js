document.addEventListener('DOMContentLoaded', () => {
    const messageBox = document.getElementById('message-box');
    const form = document.getElementById('message-form');
    const input = document.getElementById('message');

    // Fetch and render messages
    async function loadMessages() {
        try {
            const res = await fetch('/get_messages');
            const data = await res.json();

            messageBox.innerHTML = ''; // Clear old messages

            data.messages.forEach(msg => {
                const messageDiv = document.createElement('div');
                messageDiv.classList.add('message');

                if (msg.profile_pic) {
                    const img = document.createElement('img');
                    img.src = `/static/profile_pics/${msg.profile_pic}`;
                    img.className = 'message-pic';
                    img.alt = `${msg.username}'s profile pic`;
                    messageDiv.appendChild(img);
                }

                const content = document.createElement('div');
                content.innerHTML = `<strong>${msg.username}</strong><br><span>${msg.message}</span>`;
                messageDiv.appendChild(content);

                messageBox.appendChild(messageDiv);
            });

            //messageBox.scrollTop = messageBox.scrollHeight;
        } catch (err) {
            console.error('Failed to load messages:', err);
        }
    }

    // Handle form submit with fetch
    form.addEventListener('submit', async (e) => {
        e.preventDefault(); // Prevent full reload

        const message = input.value.trim();
        if (!message) return;

        const formData = new FormData();
        formData.append('message', message);

        try {
            const res = await fetch('/send_message', {
                method: 'POST',
                body: formData,
            });

            if (res.ok) {
                input.value = '';
                await loadMessages();
            } else {
                console.error('Message failed to send');
            }
        } catch (err) {
            console.error('Error sending message:', err);
        }
    });

    loadMessages();              // Initial load
    setInterval(loadMessages, 3000); // Periodic updates
});
