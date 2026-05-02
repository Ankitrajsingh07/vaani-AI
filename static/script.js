document.addEventListener("DOMContentLoaded", function () {

    // =========================
    // REGISTER
    // =========================
    function register() {
        fetch("/register", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                username: document.getElementById("username").value,
                password: document.getElementById("password").value
            })
        })
        .then(res => res.json())
        .then(data => alert(data.message));
    }

    // =========================
    // LOGIN
    // =========================
    function login() {
        let username = document.getElementById("username").value.trim();
        let password = document.getElementById("password").value.trim();

        if (!username || !password) {
            alert("Enter username and password");
            return;
        }

        fetch("/login", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ username, password })
        })
        .then(res => res.json())
        .then(data => {

            if (data.message === "Login successful") {
                document.getElementById("login-section").style.display = "none";
                document.getElementById("chat-section").style.display = "block";

                // Optional: show username
                document.querySelector("h1").innerText = "🤖 Vaani AI";
            } else {
                alert(data.message);
            }
        })
        .catch(() => alert("Login failed"));
    }

    // =========================
    // LOGOUT
    // =========================
    function logout() {
        fetch("/logout")
        .then(() => {
            document.getElementById("chat-section").style.display = "none";
            document.getElementById("login-section").style.display = "flex";
            document.getElementById("chat").innerHTML = "";
        });
    }

    // =========================
    // SPEAK
    // =========================
    function speak(text) {
        let speech = new SpeechSynthesisUtterance(text);
        speech.lang = "en-US";
        window.speechSynthesis.speak(speech);
    }

    // =========================
    // SEND MESSAGE
    // =========================
    function sendMessage(text) {

        let chat = document.getElementById("chat");
        let inputBox = document.getElementById("input");

        let input = text || inputBox.value.trim();
        if (!input) return;

        // USER MESSAGE
        let userMsg = document.createElement("p");
        userMsg.innerHTML = "<b>You:</b> " + input;
        chat.appendChild(userMsg);

        // LOADING
        let loading = document.createElement("p");
        loading.id = "loading";
        loading.innerText = "Vaani is thinking...";
        chat.appendChild(loading);

        inputBox.value = "";

        fetch("/command", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({message: input})
        })
        .then(res => res.json())
        .then(data => {

            let loading = document.getElementById("loading");
            if (loading) loading.remove();

            if (data.response === "Please login first") {
                alert("Please login first");
                return;
            }

            let botMsg = document.createElement("p");
            botMsg.innerHTML = "<b>Vaani:</b> " + data.response;
            chat.appendChild(botMsg);

            speak(data.response);

            // Open URL
            if (data.action === "open_url") {
                window.open(data.url, "_blank");
            }

            // Google Search
            if (data.action === "search_google") {
                let url = "https://www.google.com/search?q=" + encodeURIComponent(data.query);
                window.open(url, "_blank");
            }

            chat.scrollTop = chat.scrollHeight;
        })
        .catch(() => {
            let loading = document.getElementById("loading");
            if (loading) loading.remove();

            chat.innerHTML += "<p>Error occurred</p>";
        });
    }

    // =========================
    // VOICE INPUT
    // =========================
    function startVoice() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

        if (!SpeechRecognition) {
            alert("Use Google Chrome");
            return;
        }

        let recognition = new SpeechRecognition();
        let mic = document.getElementById("mic-animation");

        mic.style.opacity = "1";

        recognition.start();

        recognition.onresult = function(event) {
            let text = event.results[0][0].transcript;
            sendMessage(text);
        };

        recognition.onend = function() {
            mic.style.opacity = "0.5";
        };

        recognition.onerror = function(event) {
            console.error(event.error);
        };
    }

    // =========================
    // NAVBAR
    // =========================
    function showSection(section) {

        let isLoggedIn = document.getElementById("chat-section").style.display === "block";

        document.getElementById("chat-section").style.display = "none";
        document.getElementById("about-section").style.display = "none";
        document.getElementById("contact-section").style.display = "none";

        if (section === "chat") {
            if (!isLoggedIn) {
                alert("Please login first");
                document.getElementById("login-section").style.display = "flex";
                return;
            }
            document.getElementById("chat-section").style.display = "block";
        }

        if (section === "about") {
            document.getElementById("about-section").style.display = "block";
        }

        if (section === "contact") {
            document.getElementById("contact-section").style.display = "block";
        }
    }

    // =========================
    // CONTACT FORM
    // =========================
    function sendContactMessage() {

        let name = document.getElementById("contact-name").value;
        let email = document.getElementById("contact-email").value;
        let message = document.getElementById("contact-message").value;

        if (!name || !email || !message) {
            alert("Please fill all fields");
            return;
        }

        fetch("/contact", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ name, email, message })
        })
        .then(res => res.json())
        .then(() => {
            alert("Message sent successfully!");
        })
        .catch(() => {
            alert("Failed to send message");
        });

        document.getElementById("contact-name").value = "";
        document.getElementById("contact-email").value = "";
        document.getElementById("contact-message").value = "";
    }

    // =========================
    // MAKE FUNCTIONS GLOBAL
    // =========================
    window.register = register;
    window.login = login;
    window.logout = logout;
    window.sendMessage = sendMessage;
    window.startVoice = startVoice;
    window.showSection = showSection;
    window.sendContactMessage = sendContactMessage;

});