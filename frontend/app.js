const form = document.getElementById("chat-form");
const input = document.getElementById("user-input");
const chatArea = document.getElementById("chat-area");

// Ambil riwayat chat dari localStorage saat pertama kali
let history = JSON.parse(localStorage.getItem("chatHistory")) || [];
renderChatHistory(history);

// Tampilkan riwayat chat
function renderChatHistory(messages) {
  chatArea.innerHTML = ""; // Kosongkan dulu
  messages.forEach((msg) => {
    createBubble(msg.text, msg.sender);
  });
  scrollToBottom();
}

// Buat elemen bubble chat
function createBubble(message, sender = "user") {
  const bubble = document.createElement("div");
  bubble.className = `p-3 max-w-lg rounded-lg shadow ${
    sender === "user"
      ? "bg-indigo-600 text-white self-end ml-auto"
      : "bg-gray-200 text-gray-900 self-start mr-auto"
  }`;
  bubble.innerText = message;
  chatArea.appendChild(bubble);
}

// Scroll otomatis ke bawah
function scrollToBottom() {
  chatArea.scrollTop = chatArea.scrollHeight;
}

// Simpan riwayat ke localStorage
function saveToHistory(text, sender) {
  history.push({ text, sender });
  localStorage.setItem("chatHistory", JSON.stringify(history));
}

// Kirim pertanyaan ke backend
async function sendMessage(message) {
  createBubble(message, "user");
  saveToHistory(message, "user");
  input.value = "";

  // Tampilkan loading sementara
  const loading = document.createElement("div");
  loading.className = "italic text-gray-500";
  loading.innerText = "Bot sedang mengetik...";
  chatArea.appendChild(loading);
  scrollToBottom();

  try {
    const res = await fetch("http://127.0.0.1:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });

    const data = await res.json();
    chatArea.removeChild(loading);
    createBubble(data.reply, "bot");
    saveToHistory(data.reply, "bot");
  } catch (err) {
    chatArea.removeChild(loading);
    const errorMsg = "❌ Gagal menghubungi server.";
    createBubble(errorMsg, "bot");
    saveToHistory(errorMsg, "bot");
  }

  scrollToBottom();
}

// Event ketika form disubmit
form.addEventListener("submit", (e) => {
  e.preventDefault();
  const message = input.value.trim();
  if (message) sendMessage(message);
});

// Tombol untuk hapus riwayat
function clearHistory() {
  localStorage.removeItem("chatHistory");
  history = [];
  renderChatHistory([]);
}
