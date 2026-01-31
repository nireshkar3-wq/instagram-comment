# Instagram Comment Bot: Premium Web Dashboard 🤖💬

A high-end, responsive web application for Instagram automation. Built with **Flask-SocketIO**, **Selenium 4**, and a **Glassmorphism UI**, this bot allows you to manage multiple accounts and post comments on specific Instagram posts with real-time feedback.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Selenium 4.x](https://img.shields.io/badge/selenium-4.x-green.svg)](https://www.selenium.dev/)
[![Flask](https://img.shields.io/badge/flask-v3.0+-orange.svg)](https://flask.palletsprojects.com/)

---

## ✨ Features

- 🤖 **Auto-Driver Setup**: Uses **Selenium Manager** (built-in) to automatically install the correct ChromeDriver for your system, making it fully portable.
- 🎨 **Premium Glassmorphism UI**: A modern, interactive dashboard with frosted glass effects and dynamic gradients.
- 👥 **Multi-Account Profile Management**: Save, load, and manage multiple Instagram accounts via the browser interface.
- 🔒 **Isolated Sessions**: Each profile has its own dedicated session folder in `Instagram_session/`, ensuring privacy and preventing account cross-contamination.
- 📊 **Real-Time Activity Log**: Live log streaming from the bot to your dashboard using WebSockets (Socket.IO).
- 📱 **Fully Responsive**: Optimized for desktops, tablets, and mobile phones.
- 🛡️ **Stealth Automation**: Intelligent rate limiting, custom User-Agents, and window-size management to avoid detection.
- ⚙️ **One-Click Configuration**: Toggle headless mode and adjust comment counts directly from the UI.
- 🧹 **Automated Cleanup**: Deleting a profile automatically removes its associated session data.

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.8+**
- **Google Chrome browser** (Driver is automatically managed)
- **Git**

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/nireshkar3-wq/instagram-comment.git
cd instagram-comment

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Dashboard
```bash
python app.py
```
After running the command, open your browser and navigate to:
- **Local**: `http://localhost:5000`
- **Network (Mobile)**: `http://<your-computer-ip>:5000`

---

## 🛠️ Project Structure
```text
Instagram-Like-Comment-Bot/
├── app.py                # Flask-SocketIO Web Server
├── insta_bot.py          # Core Bot Engine (Selenium logic)
├── profiles.json         # Saved account credentials (Local only)
├── Instagram_session/    # isolated browser profile data (Git Ignore)
├── static/               # UI Assets (CSS, JS, Icons)
├── templates/            # HTML Dashboard
├── requirements.txt      # Project dependencies
└── README.md             # This file
```

---

## ⚠️ Important Safety & Usage

> [!WARNING]
> **Account Security**: Automated actions can violate Instagram's Terms of Service. 
> - Use realistic delays between comments.
> - Avoid posting duplicate spam content.
> - **HEADLESS MODE**: While stealthy, manual monitoring is recommended for new accounts to handle CAPTCHAs or 2FA.

> [!TIP]
> **Mobile Access**: You can monitor your bot's progress on your phone by connecting to the same Wi-Fi and using the host machine's IP address.

---

## 📜 Credits & License
This project is for educational purposes only. Automated botting is against Instagram's TOS. Use responsibly and at your own risk.

**Version**: 2.2.0  
**Status**: Manager-Ready / Stable / Auto-Driver
