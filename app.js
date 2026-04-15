
const API = "http://127.0.0.1:5000";


// ================= SUBMIT COMPLAINT =================
function submit(){
    let text = document.getElementById("text").value;
    let location = document.getElementById("location").value;

    if(!text || !location){
        alert("Please fill all fields");
        return;
    }

    fetch(API + "/submit", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({text, location})
    })
    .then(res => res.json())
    .then(d => {

        document.getElementById("out").innerHTML =
        "✔ Submitted ID: " + d.id;

        notify("Complaint Submitted Successfully 🚀");
    })
    .catch(err => {
        console.error(err);
        alert("Server error while submitting");
    });
}


// ================= TRACK COMPLAINT =================
function track(){
    let id = document.getElementById("cid").value;

    fetch(API + "/track/" + id)
    .then(res => res.json())
    .then(d => {

        if(d.error){
            document.getElementById("out").innerHTML =
            "❌ Complaint not found";
            return;
        }

        document.getElementById("out").innerHTML = `
            <div class="card">

                <h2>📦 Complaint Tracker</h2>

                <p><b>ID:</b> ${d.id}</p>
                <p><b>Category:</b> ${d.category}</p>
                <p><b>Priority:</b> ${d.priority}</p>
                <p><b>Department:</b> ${d.department}</p>
                <p><b>Status:</b> ${d.status}</p>
                <p><b>Location:</b> ${d.location}</p>
                <p><b>Solution:</b> ${d.solution}</p>

                <!-- 🗺️ MAP -->
                <iframe
                    width="100%"
                    height="250"
                    style="border-radius:10px"
                    src="${d.map}">
                </iframe>

            </div>
        `;
    });
}
// ================= CHATBOT =================
function chat(){
    let msg = document.getElementById("msg").value;

    if(!msg){
        alert("Type message first");
        return;
    }

    fetch(API + "/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({message: msg})
    })
    .then(res => res.json())
    .then(d => {

        console.log("CHAT RESPONSE:", d);

        document.getElementById("chatlog").innerHTML =
        "🤖 " + d.reply;

    })
    .catch(err => {
        console.error("Chat error:", err);
        document.getElementById("chatlog").innerHTML =
        "❌ Chatbot not responding";
    });
}


// ================= NOTIFICATION =================
function notify(message){

    let n = document.createElement("div");
    n.innerHTML = message;

    n.style.position = "fixed";
    n.style.bottom = "20px";
    n.style.right = "20px";
    n.style.background = "#22c55e";
    n.style.color = "white";
    n.style.padding = "10px";
    n.style.borderRadius = "8px";
    n.style.zIndex = "9999";

    document.body.appendChild(n);

    setTimeout(() => {
        n.remove();
    }, 3000);
}


// ================= LOAD DASHBOARD =================
function load(){
    fetch(API + "/complaints")
    .then(res => res.json())
    .then(d => {

        let html = "";

        d.forEach(x => {
            html += `
                <div style="margin:10px;padding:10px;background:#1e293b;color:white;border-radius:8px">
                    <b>ID:</b> ${x[0]} <br>
                    <b>Type:</b> ${x[2]} <br>
                    <b>Status:</b> ${x[6]}
                </div>
            `;
        });

        document.getElementById("data").innerHTML = html;
    });
}


// ================= STATS =================
let pieChartInstance;
let barChartInstance;

function stats(){
    fetch(API + "/stats")
    .then(res => res.json())
    .then(d => {

        document.getElementById("total").innerText = d.total;
        document.getElementById("pending").innerText = d.pending;
        document.getElementById("resolved").innerText = d.resolved;

        // 🧠 FIX: destroy old charts (VERY IMPORTANT)
        if(pieChartInstance) pieChartInstance.destroy();
        if(barChartInstance) barChartInstance.destroy();

        pieChartInstance = new Chart(document.getElementById("pieChart"), {
            type: 'pie',
            data: {
                labels: ["Pending","Resolved"],
                datasets: [{
                    data: [d.pending, d.resolved]
                }]
            }
        });

        barChartInstance = new Chart(document.getElementById("barChart"), {
            type: 'bar',
            data: {
                labels: ["Total","Pending","Resolved"],
                datasets: [{
                    data: [d.total, d.pending, d.resolved]
                }]
            }
        });

        document.getElementById("insight").innerText =
        "🔥 Most affected area: " + d.top_area;

    });
}