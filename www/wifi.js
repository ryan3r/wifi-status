let uptimes = document.querySelector(".uptime");
let table = document.querySelector("table");
let loader = document.querySelector(".loader");
let onlineStatus = document.querySelector(".online");

const PROPS = [
	"name",
	"hostname",
	"mac",
	"ip",
	"ssid",
	"router",
	"signal"
];

function signalColor(signal, ssid) {
	if(!ssid) {
		return "magenta";
	}

	signal = +signal;
	if(signal < -80) {
		return "#ff5555";
	} else if(signal < -70) {
		return "yellow";
	} else if(signal < -60) {
		return "cyan";
	} else if(signal < 0) {
		return "lightgreen";
	}

	return "white";
}

function load() {
	return Promise.race([
		fetch("/api"),
		new Promise((_, reject) => setTimeout(reject, 5000)),
	])
		.then(res => res.json())
		.then(info => {
			table.innerHTML = "";
			loader.remove();

			// Print the header
			let row = document.createElement("tr");
			table.appendChild(row);

			for(let prop of PROPS) {
				let slot = document.createElement("th");
				row.appendChild(slot);
				slot.innerText = prop;
			}

			info.clients.sort((a, b) => (a.name + "").localeCompare(b.name))

			// Print the rows
			info.clients.forEach(client => {
				let row = document.createElement("tr");
				row.style.backgroundColor = signalColor(client.signal, client.ssid);
				table.appendChild(row);

				for(let prop of PROPS) {
					let slot = document.createElement("td");
					row.appendChild(slot);
					slot.innerText = client[prop] || "---";
				}
			});

			uptimes.innerHTML = "";
			for(let uptime of info.uptimes) {
				let li = document.createElement("li");
				li.innerText = `${uptime.name}: ${uptime.uptime}`;
				uptimes.appendChild(li);
			}

			onlineStatus.innerText = info.online ? "Online" : "Offline";
			onlineStatus.style.color = info.online ? "green" : "orange";
		});
}

function loop() {
	load().catch(() => {
		onlineStatus.innerText = "Down";
		onlineStatus.style.color = "red";
	}).then(() => setTimeout(loop, 500));
}

loop();

document.querySelector(".reboot").onclick = function() {
	confirm("You are about to reboot both routers") && fetch("/api/reboot").then(r => r.text()).then(msg => alert(msg));
}
