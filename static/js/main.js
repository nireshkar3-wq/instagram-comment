document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    const botForm = document.getElementById('bot-form');
    const startBtn = document.getElementById('start-btn');
    const btnText = startBtn.querySelector('span');
    const btnLoader = startBtn.querySelector('.btn-loader');
    const logConsole = document.getElementById('log-console');
    const clearLogsBtn = document.getElementById('clear-logs');
    const statusBadge = document.getElementById('bot-status-badge');
    const statusText = document.getElementById('status-text');

    // Profile management elements
    const profileSelect = document.getElementById('profile_select');
    const toggleAddBtn = document.getElementById('toggle-add-profile');
    const addProfileForm = document.getElementById('add-profile-form');
    const saveProfileBtn = document.getElementById('save-profile-btn');
    const deleteProfileBtn = document.getElementById('delete-profile-btn');

    let isRunning = false;

    // --- Init ---
    fetchProfiles();

    // --- Socket Listeners ---
    socket.on('bot_log', (data) => {
        addLogEntry(data.message, data.level, data.timestamp);
    });

    socket.on('bot_finished', (data) => {
        setBotRunning(false);
        addLogEntry("Process finished.", "system", new Date().toLocaleTimeString());
    });

    // --- Profile Helpers ---
    async function fetchProfiles() {
        try {
            const resp = await fetch('/profiles');
            const profiles = await resp.json();

            // Clear existing except default
            profileSelect.innerHTML = '<option value="default">Default (No saved credentials)</option>';

            Object.keys(profiles).forEach(name => {
                const opt = document.createElement('option');
                opt.value = name;
                opt.textContent = name;
                profileSelect.appendChild(opt);
            });
        } catch (err) {
            console.error("Failed to fetch profiles", err);
        }
    }

    async function saveProfile() {
        const name = document.getElementById('new_profile_name').value;
        const username = document.getElementById('new_username').value;
        const password = document.getElementById('new_password').value;

        if (!name || !username || !password) {
            alert("Please fill all fields to save a profile.");
            return;
        }

        try {
            const resp = await fetch('/profiles', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, username, password })
            });

            if (resp.ok) {
                document.getElementById('new_profile_name').value = '';
                document.getElementById('new_username').value = '';
                document.getElementById('new_password').value = '';
                addProfileForm.classList.add('hidden');
                fetchProfiles();
            }
        } catch (err) {
            alert("Error saving profile: " + err.message);
        }
    }

    async function deleteProfile() {
        const name = profileSelect.value;
        if (name === 'default') return;

        if (!confirm(`Are you sure you want to delete profile "${name}"?`)) return;

        try {
            await fetch(`/profiles/${name}`, { method: 'DELETE' });
            fetchProfiles();
        } catch (err) {
            alert("Error deleting profile: " + err.message);
        }
    }

    // --- Helper Functions ---
    function addLogEntry(message, level, timestamp) {
        const entry = document.createElement('div');
        entry.className = `log-entry ${level}`;

        entry.innerHTML = `
            <span class="timestamp">[${timestamp}]</span>
            <span class="message">${message}</span>
        `;

        logConsole.appendChild(entry);
        logConsole.scrollTop = logConsole.scrollHeight;
    }

    function setBotRunning(running) {
        isRunning = running;
        startBtn.disabled = running;

        if (running) {
            btnText.textContent = "Automation Active...";
            btnLoader.classList.remove('hidden');
            statusBadge.classList.add('running');
            statusText.textContent = "Running";
        } else {
            btnText.textContent = "Start Automation";
            btnLoader.classList.add('hidden');
            statusBadge.classList.remove('running');
            statusText.textContent = "Ready";
        }
    }

    // --- Event Handlers ---
    toggleAddBtn.addEventListener('click', () => {
        addProfileForm.classList.toggle('hidden');
    });

    saveProfileBtn.addEventListener('click', saveProfile);
    deleteProfileBtn.addEventListener('click', deleteProfile);

    botForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const post_url = document.getElementById('post_url').value;
        const comment = document.getElementById('comment').value;
        const count = document.getElementById('count').value;
        const headless = document.getElementById('headless').checked;
        const profile_name = profileSelect.value;

        if (!post_url || !comment) return;

        setBotRunning(true);
        addLogEntry(`Starting bot for: ${post_url} [Profile: ${profile_name}]`, "system", new Date().toLocaleTimeString());

        try {
            const response = await fetch('/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ post_url, comment, count, headless, profile_name })
            });

            const result = await response.json();

            if (!response.ok) {
                addLogEntry(`Error: ${result.error}`, "ERROR", new Date().toLocaleTimeString());
                setBotRunning(false);
            }
        } catch (err) {
            addLogEntry(`Network Error: ${err.message}`, "ERROR", new Date().toLocaleTimeString());
            setBotRunning(false);
        }
    });

    clearLogsBtn.addEventListener('click', () => {
        logConsole.innerHTML = '';
        addLogEntry("Logs cleared.", "system", new Date().toLocaleTimeString());
    });
    // --- Password Toggle ---
    const togglePasswordBtn = document.getElementById('toggle-password-btn');
    const newPasswordField = document.getElementById('new_password');
    const eyeIcon = togglePasswordBtn.querySelector('.eye-icon');
    const eyeOffIcon = togglePasswordBtn.querySelector('.eye-off-icon');

    togglePasswordBtn.addEventListener('click', () => {
        const isPassword = newPasswordField.type === 'password';
        newPasswordField.type = isPassword ? 'text' : 'password';

        eyeIcon.classList.toggle('hidden', isPassword);
        eyeOffIcon.classList.toggle('hidden', !isPassword);
    });
});
