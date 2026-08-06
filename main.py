<!DOCTYPE html>
<html lang="am">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ጋሻዬ ሀዋሳ - የእቁብ መመዝገቢያ ደብተር</title>
<style>
body {
font-family: 'Segoe UI', Arial, sans-serif;
background-color: #f4f6f9;
margin: 0;
padding: 10px;
text-align: center;
}
header {
background-color: #2c3e50;
color: white;
padding: 15px;
border-radius: 10px;
margin-bottom: 15px;
}
h1 { margin: 0; font-size: 20px; }
.controls {
margin: 15px 0;
display: flex;
justify-content: center;
gap: 10px;
align-items: center;
flex-wrap: wrap;
}
select, input {
padding: 10px;
border-radius: 5px;
border: 1px solid #ccc;
font-size: 14px;
}
.grid-container {
display: grid;
grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
gap: 8px;
max-width: 100%;
margin: 0 auto;
}
.ticket {
background-color: #2ecc71;
color: white;
padding: 12px 5px;
border-radius: 6px;
cursor: pointer;
font-weight: bold;
font-size: 13px;
box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.ticket.booked {
background-color: #e74c3c;
}
.ticket.pending {
background-color: #f39c12;
}
.ticket-details {
font-size: 10px;
display: block;
margin-top: 3px;
font-weight: normal;
background: rgba(0,0,0,0.15);
border-radius: 3px;
padding: 1px;
}
.modal {
display: none;
position: fixed;
top: 0; left: 0; width: 100%; height: 100%;
background-color: rgba(0,0,0,0.5);
justify-content: center;
align-items: center;
z-index: 1000;
}
.modal-content {
background-color: white;
padding: 20px;
border-radius: 10px;
width: 90%;
max-width: 360px;
text-align: left;
max-height: 90vh;
overflow-y: auto;
}
.modal-content input, .modal-content select {
width: 100%;
margin: 5px 0 12px 0;
box-sizing: border-box;
}
.bank-info-box {
background: #f8f9fa;
border: 1px dashed #2980b9;
padding: 10px;
border-radius: 5px;
font-size: 12px;
margin-bottom: 12px;
color: #2c3e50;
line-height: 1.5;
}
.modal-btns {
display: flex;
justify-content: flex-end;
gap: 10px;
}
.btn {
padding: 8px 15px;
border: none;
border-radius: 5px;
cursor: pointer;
font-weight: bold;
}
.btn-submit { background-color: #2ecc71; color: white; width: 100%; }
.btn-cancel { background-color: #95a5a6; color: white; }
.btn-danger { background-color: #c0392b; color: white; width: 100%; margin-top: 10px; }

#lockScreen {
position: fixed;
top:0; left:0; width:100%; height:100%;
background-color: #2c3e50;
color: white;
display: flex;
flex-direction: column;
justify-content: center;
align-items: center;
z-index: 2000;
}
.pin-container {
position: relative;
width: 220px;
margin-bottom: 15px;
}
.pin-container input {
width: 100%;
padding-right: 40px;
text-align: center;
font-size: 18px;
box-sizing: border-box;
}
.eye-icon {
position: absolute;
right: 10px;
top: 50%;
transform: translateY(-50%);
cursor: pointer;
font-size: 18px;
user-select: none;
}
</style>
</head>
<body>

<div id="lockScreen">
<h2 id="lockTitle">መተግበሪያው ተቆልፏል</h2>
<p id="lockSub">እባክዎ ሚስጥራዊ የፒን ቁጥርዎን ያስገቡ</p>
<div class="pin-container">
<input type="password" id="pinInput" placeholder="የፒን ቁጥር ያስገቡ">
<span class="eye-icon" id="toggleEye" onclick="togglePINVisibility()">👁️‍🗨️</span>
</div>
<button class="btn btn-submit" style="width:220px; padding:12px;" onclick="checkPIN()">ደብተሩን ክፈት</button>
</div>

<div id="mainApp" style="display:none;">
<header>
<h1>ጋሻዬ ሀዋሳ - የእቁብ መመዝገቢያ ደብተር</h1>
<button class="btn btn-cancel" style="font-size:11px; margin-top:5px; padding:4px 8px;" onclick="lockAppNow()">አፑን ቆልፍ</button>
</header>
<div class="controls">
<label><b>የእቁብ ድርሻ ብዛት፦</b></label>
<select id="rangeSelect" onchange="generateTickets()">
<option value="50">50 ድርሻዎች</option>
<option value="100">100 ድርሻዎች</option>
<option value="200" selected>200 ድርሻዎች</option>
</select>
</div>
<div class="grid-container" id="ticketGrid"></div>
</div>

<div class="modal" id="bookingModal">
<div class="modal-content">
<h3 id="modalTitle" style="margin-top:0; font-size:16px;">ሰው ለመመዝገብ</h3>

<div class="bank-info-box">
<b>የክፍያ አካውንቶች (ስም: ጋሻዬ በእጅጉ ሄርጎ)፦</b><br>
• ቴሌብር: <b>0916039015</b><br>
• ንግድ ባንክ (CBE): <b>100070780201</b><br>
• አቢሲኒያ ባንክ: <b>54071628</b><br>
• ንብ ባንክ: <b>7000106022734</b><br>
• ዳሽን ባንክ: <b>5121355332011</b>
</div>

<label>የአባሉ ሙሉ ስም፦</label>
<input type="text" id="userName" placeholder="ስም ያስገቡ">

<label>ስልክ ቁጥር፦</label>
<input type="tel" id="userPhone" placeholder="09........">

<label>እቁቡ የሚቆይበት ሳምንት (ከ 1 እስከ 110)፦</label>
<select id="weekSelect" style="width:100%; margin:5px 0 12px 0; padding:10px; border-radius:5px;"></select>

<label>የክፍያ ሁኔታ እና ባንክ፦</label>
<select id="payStatus" style="width:100%; margin:5px 0 15px 0; padding:10px; border-radius:5px;">
<option value="በቴሌብር ከፍሏል">በቴሌብር (0916039015)</option>
<option value="በንግድ ባንክ ከፍሏል">በንግድ ባንክ (100070780201)</option>
<option value="በአቢሲኒያ ባንክ ከፍሏል">በአቢሲኒያ ባንክ (54071628)</option>
<option value="በንብ ባንክ ከፍሏል">በንብ ባንክ (7000106022734)</option>
<option value="በዳሽን ባንክ ከፍሏል">በዳሽን ባንክ (5121355332011)</option>
<option value="በካሽ ከፍሏል">በካሽ (Cash)</option>
<option value="ያልከፈለ">አልከፈለም</option>
</select>

<div class="modal-btns">
<button class="btn btn-cancel" onclick="closeModal()">ተውት</button>
<button class="btn btn-submit" onclick="submitBooking()">ክፍያ ፈጽሞ መዝግብ</button>
</div>

<div id="deleteSection" style="display:none;">
<hr style="margin:15px 0 10px 0;">
<button class="btn btn-danger" onclick="deleteBooking()">በሙሉ አጥፋ (Erase)</button>
</div>
</div>
</div>

<script>
let currentSelectedTicket = null;
let bookedTickets = JSON.parse(localStorage.getItem('gashayeBookings')) || {};
let savedPIN = localStorage.getItem('gashayeAppPIN');

window.onload = function() {
    if (!savedPIN) {
        document.getElementById('lockTitle').innerText = "አዲስ የፒን ቁጥር ያዘጋጁ";
        document.getElementById('lockSub').innerText = "ደብተሩን ለመቆለፍ አዲስ ሚስጥራዊ ቁጥር ይፍጠሩ";
    }
    populateWeeks();
    loadBookingsFromServer();
};

function populateWeeks() {
    const weekSelect = document.getElementById('weekSelect');
    weekSelect.innerHTML = '';
    for(let w = 1; w <= 110; w++) {
        let opt = document.createElement('option');
        opt.value = w;
        opt.innerText = `ሳምንት ${w} (ከ 110)`;
        weekSelect.appendChild(opt);
    }
}

async function loadBookingsFromServer() {
    try {
        const res = await fetch('/api/get-bookings');
        const data = await res.json();
        if(data && data.bookings) {
            bookedTickets = data.bookings;
            localStorage.setItem('gashayeBookings', JSON.stringify(bookedTickets));
        }
    } catch(e) {
        console.log("Local storage used");
    }
    generateTickets();
}

function togglePINVisibility() {
    const pinInput = document.getElementById('pinInput');
    const eyeIcon = document.getElementById('toggleEye');
    if (pinInput.type === 'password') {
        pinInput.type = 'text';
        eyeIcon.innerText = '👁️';
    } else {
        pinInput.type = 'password';
        eyeIcon.innerText = '👁️‍🗨️';
    }
}

function checkPIN() {
    const input = document.getElementById('pinInput').value;
    if (!input) { alert('እባክዎ ቁጥር ያስገቡ!'); return; }
    if (!savedPIN) {
        localStorage.setItem('gashayeAppPIN', input);
        savedPIN = input;
        alert('የመቆለፊያ ፒን ቁጥርዎ በተሳካ ሁኔታ ተፈጥሯል!');
        enterApp();
    } else if (input === savedPIN) {
        enterApp();
    } else {
        alert('የተሳሳተ የፒን ቁጥር ነው! እንደገና ይሞክሩ።');
    }
    document.getElementById('pinInput').value = '';
    document.getElementById('pinInput').type = 'password';
    document.getElementById('toggleEye').innerText = '👁️‍🗨️';
}

function enterApp() {
    document.getElementById('lockScreen').style.display = 'none';
    document.getElementById('mainApp').style.display = 'block';
    generateTickets();
}

function lockAppNow() {
    document.getElementById('lockScreen').style.display = 'flex';
    document.getElementById('mainApp').style.display = 'none';
}

function generateTickets() {
    const grid = document.getElementById('ticketGrid');
    const range = document.getElementById('rangeSelect').value;
    grid.innerHTML = '';
    for (let i = 1; i <= range; i++) {
        const ticket = document.createElement('div');
        ticket.className = 'ticket';
        ticket.id = 'ticket-' + i;
        
        const bData = bookedTickets[i];
        if (bData) {
            if (bData.status === 'approved') {
                ticket.classList.add('booked');
                ticket.innerHTML = `${bData.name}<br>${bData.phone} <span class="ticket-details">ድርሻ ${i} [ሳምንት ${bData.week}]</span>`;
            } else {
                ticket.classList.add('pending');
                ticket.innerHTML = `${bData.name}<br>ክፍያ በመረጋገጥ ላይ... <span class="ticket-details">ሳምንት ${bData.week}</span>`;
            }
        } else {
            ticket.innerHTML = `ድርሻ ${i} <span class="ticket-details">ክፍት ነው</span>`;
        }
        ticket.onclick = () => openModal(i);
        grid.appendChild(ticket);
    }
}

function openModal(ticketNumber) {
    currentSelectedTicket = ticketNumber;
    const existingData = bookedTickets[ticketNumber];
    if (existingData) {
        document.getElementById('modalTitle').innerText = `የእቁብ ድርሻ ${ticketNumber} (የተመዘገበ መረጃ)`;
        document.getElementById('userName').value = existingData.name;
        document.getElementById('userPhone').value = existingData.phone;
        document.getElementById('weekSelect').value = existingData.week || 1;
        document.getElementById('payStatus').value = existingData.pay;
        document.getElementById('deleteSection').style.display = 'block';
    } else {
        document.getElementById('modalTitle').innerText = `የእቁብ ድርሻ ${ticketNumber} ላይ መመዝገቢያ`;
        document.getElementById('userName').value = '';
        document.getElementById('userPhone').value = '';
        document.getElementById('weekSelect').value = '1';
        document.getElementById('payStatus').value = 'በቴሌብር ከፍሏል';
        document.getElementById('deleteSection').style.display = 'none';
    }
    document.getElementById('bookingModal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('bookingModal').style.display = 'none';
}

async function submitBooking() {
    const name = document.getElementById('userName').value.trim();
    const phone = document.getElementById('userPhone').value.trim();
    const week = document.getElementById('weekSelect').value;
    const pay = document.getElementById('payStatus').value;

    if (!name || !phone) {
        alert('እባክዎ ሙሉ ስም እና ስልክ ቁጥር ያስገቡ!');
        return;
    }

    try {
        const response = await fetch('/api/save-booking', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                ticket_number: currentSelectedTicket,
                name: name,
                phone: phone,
                week: week,
                pay_status: pay
            })
        });
        const result = await response.json();
        if(result.status === 'success') {
            alert('ክፍያዎ እና ምዝገባዎ በትክክል ተልኳል! አድሚኑ ያረጋግጠዋል።');
            bookedTickets[currentSelectedTicket] = { name: name, phone: phone, week: week, pay: pay, status: 'pending' };
            localStorage.setItem('gashayeBookings', JSON.stringify(bookedTickets));
            generateTickets();
            closeModal();
        } else {
            alert('ስህተት ተፈጥሯል');
        }
    } catch(e) {
        alert('የኔትወርክ ስህተት');
    }
}

async function deleteBooking() {
    if (confirm(`ድርሻ ${currentSelectedTicket} ላይ ያለውን የእቁብ መረጃ ማጥፋት ይፈልጋሉ?`)) {
        try {
            await fetch('/api/delete-booking', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ticket_number: currentSelectedTicket })
            });
            delete bookedTickets[currentSelectedTicket];
            localStorage.setItem('gashayeBookings', JSON.stringify(bookedTickets));
            generateTickets();
            closeModal();
        } catch(e) {
            alert('ማጥፋት አልተቻለም');
        }
    }
}
</script>
</body>
</html>
