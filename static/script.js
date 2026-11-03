// Frontend logic: send the user's message to /api/chat and show the reply.

const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");
const button = document.getElementById("send-btn");
const messages = document.getElementById("messages");

// Add one message bubble to the chat window.
function addMessage(text, type) {
  const div = document.createElement("div");
  div.className = `msg msg--${type}`;
  div.textContent = text; // textContent (not innerHTML) prevents XSS
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault(); // stop the page from reloading

  const message = input.value.trim();
  if (!message) return;

  addMessage(message, "user");
  input.value = "";
  button.disabled = true;

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    const data = await response.json();

    if (!response.ok) {
      addMessage(data.error || "Something went wrong.", "error");
    } else {
      addMessage(data.answer, "bot");
    }
  } catch (err) {
    addMessage("Could not reach the server. Is it running?", "error");
  } finally {
    button.disabled = false;
    input.focus();
  }
});

addMessage("Hi! Ask me a health question. (Try: What is a fever?)", "bot");
