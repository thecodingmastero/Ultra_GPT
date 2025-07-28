const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const priceBtn = document.getElementById("price-btn");

function addMessage(text, sender) {
  const div = document.createElement("div");
  div.className = "message " + sender;
  div.textContent = text;
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function clearInput() {
  userInput.value = "";
}

async function sendMessage() {
  const text = userInput.value.trim();
  if (!text) return;

  addMessage(text, "user");
  clearInput();
  addMessage("Ultra-GPT is typing...", "bot");

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });

    const data = await res.json();
    chatBox.lastChild.remove();

    if (data.response) {
      addMessage(data.response, "bot");
    } else {
      addMessage("Error: No response from backend", "bot");
    }
  } catch (err) {
    chatBox.lastChild.remove();
    addMessage("Network error", "bot");
  }
}

async function getPrice() {
  const symbol = userInput.value.trim().toUpperCase();
  if (!symbol) return;

  addMessage(`Checking price for ${symbol}...`, "user");
  clearInput();
  addMessage("Fetching price...", "bot");

  try {
    const res = await fetch(`/price?symbol=${encodeURIComponent(symbol)}`);
    const data = await res.json();
    chatBox.lastChild.remove();

    if (data.price) {
      addMessage(
        `${data.symbol} price is $${data.price} (source: ${data.source})`,
        "bot"
      );
    } else if (data.error) {
      addMessage(`Error: ${data.error}`, "bot");
    } else {
      addMessage("Could not fetch price.", "bot");
    }
  } catch (err) {
    chatBox.lastChild.remove();
    addMessage("Network error", "bot");
  }
}

sendBtn.addEventListener("click", sendMessage);
priceBtn.addEventListener("click", getPrice);

userInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendMessage();
});
