const games=[
{name:"Fortnite",icon:"🪂",description:"Cloud-streaming integration placeholder"},
{name:"Rocket League",icon:"🚗",description:"Cloud-streaming integration placeholder"},
{name:"Fall Guys",icon:"🏃",description:"Cloud-streaming integration placeholder"},
{name:"Game Test",icon:"🕹️",description:"Safe local prototype session"}
];

let currentSession=null;
let timerHandle=null;
const gamesEl=document.getElementById("games"),searchEl=document.getElementById("search"),countEl=document.getElementById("gameCount");
const sessionPanel=document.getElementById("sessionPanel"),sessionTitle=document.getElementById("sessionTitle"),sessionId=document.getElementById("sessionId");
const stream=document.getElementById("stream"),streamStatus=document.getElementById("streamStatus"),streamDetail=document.getElementById("streamDetail");
const controllerState=document.getElementById("controllerState"),micState=document.getElementById("micState"),timerBadge=document.getElementById("timerBadge");

function renderGames(filter=""){
 const list=games.filter(g=>g.name.toLowerCase().includes(filter.toLowerCase()));
 countEl.textContent=`${list.length} game${list.length===1?"":"s"}`;
 gamesEl.innerHTML=list.map(g=>`<article class="card"><div><div class="art">${g.icon}</div><h3>${g.name}</h3><p>${g.description}</p></div><button class="play" data-game="${games.indexOf(g)}">▶ Play</button></article>`).join("");
 gamesEl.querySelectorAll(".play").forEach(b=>b.addEventListener("click",()=>startSession(games[Number(b.dataset.game)])));
}

async function startSession(game){
 stopTimer();
 sessionPanel.classList.remove("hidden");
 sessionTitle.textContent=game.name;
 streamStatus.textContent="Starting local cloud session...";
 streamDetail.textContent="Contacting the NOVOS Cloud test server...";
 sessionId.textContent="connecting";
 sessionPanel.scrollIntoView({behavior:"smooth",block:"center"});

 try{
   const r=await fetch("/api/session/start",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({game:game.name})});
   if(!r.ok) throw new Error("Server unavailable");
   const data=await r.json();
   currentSession=data.session;
   sessionId.textContent=currentSession.id;
   streamStatus.textContent="Server allocated";
   streamDetail.textContent="Local session is ready. A real game stream will plug in here later.";
   updateTimer(data.maxSeconds);
   timerHandle=setInterval(refreshSession,1000);
 }catch(e){
   currentSession=null;
   sessionId.textContent="offline";
   streamStatus.textContent="Test server not connected";
   streamDetail.textContent="Run server.py locally to test real session management. The UI remains usable in demo mode.";
   updateTimer(3600);
   timerHandle=setInterval(()=>updateTimer(parseInt(timerBadge.dataset.seconds||"3600")-1),1000);
 }
}

async function refreshSession(){
 if(!currentSession)return;
 try{
   const r=await fetch(`/api/session/${currentSession.id}`);
   const data=await r.json();
   updateTimer(data.remainingSeconds);
   if(!data.session.active){
     streamStatus.textContent="Session ended";
     streamDetail.textContent=data.session.expired?"The 1-hour session limit was reached.":"The session was stopped.";
     stopTimer();
   }
 }catch{}
}

function updateTimer(seconds){
 seconds=Math.max(0,Number(seconds)||0);
 timerBadge.dataset.seconds=seconds;
 const h=Math.floor(seconds/3600),m=Math.floor((seconds%3600)/60),s=seconds%60;
 timerBadge.textContent=`⏱ ${h?String(h).padStart(2,"0")+":":""}${String(m).padStart(2,"0")}:${String(s).padStart(2,"0")}`;
 if(seconds<=300) timerBadge.style.borderColor="#8b5a2b";
}

function stopTimer(){if(timerHandle){clearInterval(timerHandle);timerHandle=null}}

document.getElementById("stopBtn").addEventListener("click",async()=>{
 if(currentSession){
   try{await fetch("/api/session/stop",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({sessionId:currentSession.id})})}catch{}
 }
 stopTimer();currentSession=null;sessionPanel.classList.add("hidden");
});

document.getElementById("fullscreenBtn").addEventListener("click",async()=>{
 try{
   if(!document.fullscreenElement) await stream.requestFullscreen();
   else await document.exitFullscreen();
 }catch{alert("Fullscreen was blocked by the browser.");}
});

searchEl.addEventListener("input",e=>renderGames(e.target.value));

document.getElementById("micBtn").addEventListener("click",async()=>{
 if(!navigator.mediaDevices?.getUserMedia){micState.textContent="Browser unavailable";return}
 try{
   const s=await navigator.mediaDevices.getUserMedia({audio:true});
   s.getTracks().forEach(t=>t.stop());
   micState.textContent="Permission granted";
   document.getElementById("micBtn").textContent="🎤 Microphone: Ready";
 }catch{micState.textContent="Permission denied";}
});

const modal=document.getElementById("controllerModal");
document.getElementById("controllerBtn").addEventListener("click",()=>{
 modal.classList.remove("hidden");
 pollController();
});
document.getElementById("closeController").addEventListener("click",()=>modal.classList.add("hidden"));
modal.addEventListener("click",e=>{if(e.target===modal)modal.classList.add("hidden")});

function pollController(){
 if(modal.classList.contains("hidden"))return;
 const pads=navigator.getGamepads?navigator.getGamepads():[];
 const pad=Array.from(pads).find(Boolean);
 const details=document.getElementById("controllerDetails");
 if(!pad){
   details.textContent="No controller detected. Connect a controller, then press a button.";
   controllerState.textContent="Not detected";
 }else{
   controllerState.textContent="Connected";
   const a=pad.buttons.map((b,i)=>b.pressed?`Button ${i}`:"").filter(Boolean).join(", ");
   details.textContent=`${pad.id} • ${pad.buttons.length} buttons • ${a||"No buttons pressed"}`;
   document.getElementById("leftStick").textContent=`${pad.axes?.[0]?.toFixed(1)||"0"},${pad.axes?.[1]?.toFixed(1)||"0"}`;
   document.getElementById("rightStick").textContent=`${pad.axes?.[2]?.toFixed(1)||"0"},${pad.axes?.[3]?.toFixed(1)||"0"}`;
   document.getElementById("btnA").style.transform=pad.buttons[0]?.pressed?"scale(1.2)":"";
   document.getElementById("btnB").style.transform=pad.buttons[1]?.pressed?"scale(1.2)":"";
   document.getElementById("btnX").style.transform=pad.buttons[2]?.pressed?"scale(1.2)":"";
   document.getElementById("btnY").style.transform=pad.buttons[3]?.pressed?"scale(1.2)":"";
 }
 requestAnimationFrame(pollController);
}
window.addEventListener("gamepadconnected",()=>controllerState.textContent="Connected");
window.addEventListener("gamepaddisconnected",()=>controllerState.textContent="Disconnected");

renderGames();
