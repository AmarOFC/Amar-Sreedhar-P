// 1. Generate Starry Sky
const universe = document.getElementById("universe");
for (let i = 0; i < 100; i++) {
  let star = document.createElement("div");
  star.className = "star";
  let size = Math.random() * 2.5 + 0.5;
  star.style.width = size + "px";
  star.style.height = size + "px";
  star.style.top = Math.random() * 100 + "%";
  star.style.left = Math.random() * 100 + "%";
  star.style.animationDuration = Math.random() * 3 + 2 + "s";
  star.style.animationDelay = Math.random() * 5 + "s";
  universe.appendChild(star);
}

// 2. Logic Variables & UI Selectors
// UPDATE THIS URL TO YOUR LIVE RENDER URL
const API_BASE_URL = "https://amar-sreedhar-p.onrender.com"; 

let currentSessionId = "session_" + Math.random().toString(36).substr(2, 9);
const modal = document.getElementById("auth-modal");
const chatContainer = document.querySelector(".chat-container");
const authMessage = document.getElementById("auth-message");
const inputField = document.getElementById("user-input");
const chatBox = document.getElementById("chat-box");

// Allow 'Enter' key to send message
inputField.addEventListener("keypress", function (event) {
  if (event.key === "Enter") {
    event.preventDefault();
    sendMessage();
  }
});

// 3. Registration Logic (Connecting to Render /register)
async function registerUser() {
  const email = document.getElementById("reg-email").value;
  const password = document.getElementById("reg-password").value;
  const dob = document.getElementById("reg-dob").value;

  if (!email || !password || !dob) {
    authMessage.innerText = "Please provide all details to proceed.";
    return;
  }

  authMessage.style.color = "#a8e6cf";
  authMessage.innerText = "Consulting the ephemeris...";

  try {
    // UPDATED: Now points to Render instead of 127.0.0.1
    const response = await fetch(`${API_BASE_URL}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: email,
        password: password,
        birth_date: dob,
      }),
    });

    const data = await response.json();

    if (response.ok) {
      modal.style.opacity = "0";
      setTimeout(() => {
        modal.style.display = "none";
        chatContainer.style.display = "flex";

        appendMessage(
          `Welcome, traveler. I see the radiant energy of a ${data.sun_sign} within you. What life events or cosmic energies would you like me to forecast for you today?`,
          "bot",
        );
      }, 500);
    } else {
      authMessage.style.color = "#ffb7b2";
      authMessage.innerText = data.error || "The stars are misaligned. Try again.";
    }
  } catch (error) {
    console.error("Connection Error:", error);
    authMessage.style.color = "#ffb7b2";
    authMessage.innerText = "Could not reach the celestial brain on Render.";
  }
}

// 4. Chat Logic (Connecting to Render /chat)
async function sendMessage() {
  let text = inputField.value.trim();
  if (text === "") return;

  appendMessage(text, "user");
  inputField.value = "";

  try {
    // UPDATED: Now points to Render instead of 127.0.0.1
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        session_id: currentSessionId,
      }),
    });

    const data = await response.json();

    if (data.response) {
      appendMessage(data.response, "bot");
    } else {
      appendMessage(
        "The celestial signals are currently obscured. Speak again later.",
        "bot",
      );
    }
  } catch (error) {
    console.error("Chat Connection Error:", error);
    appendMessage(
      "My connection to the celestial ether is disrupted. Check your Render service.",
      "bot",
    );
  }
}

// 5. UI Helper Function
function appendMessage(text, sender) {
  const msgDiv = document.createElement("div");
  msgDiv.className = `msg ${sender}`;
  msgDiv.innerText = text;
  chatBox.appendChild(msgDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
}
