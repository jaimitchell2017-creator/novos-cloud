const games = [
  {name:"Fortnite", icon:"🪂", description:"Cloud-streaming integration placeholder"},
  {name:"Rocket League", icon:"🚗", description:"Cloud-streaming integration placeholder"},
  {name:"Fall Guys", icon:"🏃", description:"Cloud-streaming integration placeholder"},
  {name:"Game Test", icon:"🕹️", description:"Safe local prototype session"}
];

const gamesEl = document.getElementById("games");
const searchEl = document.getElementById("search");
const countEl = document.getElementById("gameCount");
const sessionPanel = document.getElementById("sessionPanel");
const sessionTitle = document.getElementById("sessionTitle");
const streamStatus = document.getElementById("streamStatus");
const streamDetail = document.getElementById("streamDetail");
const controllerState = document.getElementById("controllerState");
const micState = document.getElementById("micState");

function renderGames(filter = "") {
  const list = games.filter(g => g.name.toLowerCase().includes(filter.toLowerCase()));
  countEl.textContent = `${list.length} game${list.length === 1 ? "" : "s"}`;
  gamesEl.innerHTML = list.map((g, i) => `
    <article class="card">
      <div>
        <div class="art">${g.icon}</div>
        <h3>${g.name}</h3>
        <p>${g.description}</p>
      </div>
      <button class="play" data-game="${i}">▶ Play</button>
    </article>
  `).join("");

  gamesEl.querySelectorAll(".play").forEach(btn => {
    btn.addEventListener("click", () => startSession(games[Number(btn.dataset.game)]));
  });
}

function startSession(game) {
  sessionPanel.classList.remove("hidden");
  sessionTitle.textContent = game.name;
  streamStatus.textContent = "Finding an available gaming server...";
  streamDetail.textContent = "Prototype session — no real game is being streamed yet.";
  sessionPanel.scrollIntoView({behavior:"smooth", block:"center"});

  setTimeout(() => {
    streamStatus.textContent = "Server allocated";
    streamDetail.textContent = "A real backend would now establish the low-latency game stream.";
  }, 1300);

  setTimeout(() => {
    streamStatus.textContent = "Ready for streaming";
    streamDetail.textContent = "This test UI is ready for a WebRTC/streaming backend.";
  }, 2600);
}

document.getElementById("stopBtn").addEventListener("click", () => {
  sessionPanel.classList.add("hidden");
});

searchEl.addEventListener("input", e => renderGames(e.target.value));

document.getElementById("micBtn").addEventListener("click", async () => {
  if (!navigator.mediaDevices?.getUserMedia) {
    micState.textContent = "Browser unavailable";
    return;
  }
  try {
    const stream = await navigator.mediaDevices.getUserMedia({audio:true});
    stream.getTracks().forEach(track => track.stop());
    micState.textContent = "Permission granted";
    document.getElementById("micBtn").textContent = "🎤 Microphone: Ready";
  } catch {
    micState.textContent = "Permission denied";
  }
});

document.getElementById("controllerBtn").addEventListener("click", () => {
  const pads = navigator.getGamepads ? navigator.getGamepads() : [];
  const connected = Array.from(pads).some(Boolean);
  controllerState.textContent = connected ? "Connected" : "No controller detected";
});

window.addEventListener("gamepadconnected", () => {
  controllerState.textContent = "Connected";
});

window.addEventListener("gamepaddisconnected", () => {
  controllerState.textContent = "Disconnected";
});

renderGames();
