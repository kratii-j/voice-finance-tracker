//  Voice Assistant Frontend (logic behind)
const voiceBtn = document.getElementById("voiceBtn");
const voiceStatus = document.createElement("div");
voiceStatus.className = "voice-status";
document.body.appendChild(voiceStatus);

let recognition;

if ("webkitSpeechRecognition" in window) {
  recognition = new webkitSpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.lang = "en-IN";

  recognition.onstart = () => {
    voiceBtn.classList.add("listening");
    voiceStatus.textContent = "Listening...";
    voiceStatus.style.display = "block";
  };

  recognition.onend = () => {
    voiceBtn.classList.remove("listening");
    setTimeout(() => voiceStatus.style.display = "none", 1000);
  };

  recognition.onresult = async (event) => {
    const transcript = event.results[0][0].transcript;
    voiceStatus.textContent = `Heard: "${transcript}"`;
    const response = await fetch("/api/voice_command", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ command: transcript })
    });

    const data = await response.json();
    voiceStatus.textContent = data.reply || "Command processed.";

    // Optional: make it speak the reply
    if ("speechSynthesis" in window && data.reply) {
      const utter = new SpeechSynthesisUtterance(data.reply);
      speechSynthesis.speak(utter);
    }
  };
}

voiceBtn.addEventListener("click", () => {
  if (recognition) recognition.start();
  else alert("Voice recognition not supported in this browser.");
});
