<!DOCTYPE html>
<html lang="am">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ጋሻዬ ሀዋሳ - የራዕይ እቁብ መመዝገቢያ</title>
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
            transition: all 0.2s;
        }
        .ticket.selected {
            background-color: #f39c12 !important;
            border: 2px dashed #fff;
        }
        .ticket.booked {
            background-color: #e74c3c;
            cursor: not-allowed;
        }
        .ticket.pending {
            background-color: #f1c40f;
            color: #2c3e50;
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
        .modal-btns {
            display: flex;
            justify-content: flex-end;
            gap: 10px;
        }
        .btn {
            padding: 10px 15px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
        }
        .btn-submit { background-color: #2ecc71; color: white; width: 100%; }
        .btn-cancel { background-color: #95a5a6; color: white; }
        .btn-chapa { background-color: #1abc9c; color: white; width: 100%; margin-top: 5px; }
        
        .bank-info-box {
            background: #eef2f7;
            border-left: 4px solid #2c3e50;
            padding: 10px;
            font-size: 12px;
            margin-bottom: 10px;
            border-radius: 4px;
        }

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
        .floating-action {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #2ecc71;
            color: white;
            padding: 12px 20px;
            border-radius: 30px;
            font-weight: bold;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            cursor: pointer;
            display: none;
            z-index: 500;
        }
    </style>
</head>
<body>

    <!-- መቆለፊያ ስክሪን -->
    <div id="lockScreen">
        <h2 id="lockTitle">መተግበሪያው ተቆልፏል</h2>
        <p id="lockSub">እባክዎ ሚስጥራዊ የፒን ቁጥርዎን ያስገቡ</p>
        <div class="pin-container">
            <input type="password" id="pinInput" placeholder="የፒን ቁጥር ያስገቡ">
            <span class="eye-icon" id="toggleEye" onclick="togglePINVisibility()">👁️‍🗨️</span>
        </div>
        <button class="btn btn-submit" style="width:220px;" onclick="checkPIN()">ደብተሩን ክፈት</button>
    </div>

    <!-- ዋናው የአፕሊኬሽን ክፍል -->
    <div id="mainApp" style="display:none;">
        <header>
            <h1>ጋሻዬ ሀዋሳ - የእቁብ መመዝገቢያ ደብተር</h1>
            <button class="btn btn-cancel" style="font-size:11px; margin-top:5px; padding:4px 8px;" onclick="lockAppNow()">አፑን ቆልፍ</button>
        </header>

        <div class="controls">
            <label><b>የእቁብ ቁጥር መጠን፦</b></label>
            <select id="rangeSelect" onchange="generateTickets()">
                <option value="100">100 ቁጥሮች</option>
                <option value="1000">1,000 ቁጥሮች</option>
                <option value="5000">5,000 ቁጥሮች</option>
                <option value="10000">10,000 ቁጥሮች</option>
            </select>
            <span style="font-size: 12px; color: #555;">💡 ብዙ ቁጥሮችን በአንድ ላይ መምረጥ ይቻላል!</span>
        </div>

        <div class="grid-container" id="ticketGrid"></div>
    </div>

    <!-- ተጠቃሚው የሚመዘገብበት እና ብዙ ቁጥሮችን የሚያስተዳድርበት ፎርም -->
    <div class="modal" id="bookingModal">
        <div class="modal-content">
            <h3 id="modalTitle" style="margin-top:0; font-size:16px; color:#2c3e50;">እቁብ ምዝገባ</h3>
            
            <div class="bank-info-box">
                <b>የባንክ ሂሳብ መረጃ:</b><br>
                • ባንክ: CBE (100070780201)<br>
                • ስም: ጋሻዬ በጅጉ ሄሪጎ<br>
                • ስልክ: 0916039015
            </div>

            <label><b>የተመረጡ ቁጥሮች፦</b></label>
            <input type="text" id="selectedTicketsDisplay" readonly style="background:#eef2f7; font-weight:bold;">

            <label><b>የአባሉ ሙሉ ስም፦</b></label>
            <input type="text" id="userName" placeholder="ሙሉ ስምዎን ያስገቡ">
            
            <label><b>ስልክ ቁጥር፦</b></label>
            <input type="tel" id="userPhone" placeholder="09........">
            
            <label><b>የክፍያ ሁኔታ፦</b></label>
            <select id="payStatus">
                <option value="ንግድ ባንክ (በስክሪንሾት)">በንግድ ባንክ (ስክሪንሾት ማያያዝ)</option>
                <option value="ቴሌብር (በስክሪንሾት)">በቴሌብር (ስክሪንሾት ማያያዝ)</option>
                <option value="በቻፓ (Chapa Online)">በኦንላይን (Chapa 💳)</option>
            </select>

            <div id="screenshotSection" style="margin-bottom: 12px;">
                <label><b>የክፍያ ማረጋገጫ (ስክሪንሾት ፎቶ) ይጫኑ፦</b></label>
                <input type="file" id="paymentScreenshot" accept="image/*" style="padding: 5px; font-size: 12px;">
            </div>

            <div class="modal-btns" style="margin-top: 15px;">
                <button class="btn btn-cancel" onclick="closeModal()">ተውት</button>
                <button class="btn btn-submit" onclick="submitUserBooking()">በባንክ/ካሽ መዝግብ</button>
            </div>
            <button class="btn btn-btn-chapa" onclick="payWithChapa()" style="background:#1abc9c; color:white; width:100%; margin-top:8px; padding:10px; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">በቻፓ (Chapa) በቀጥታ ክፈል ⚡</button>
        </div>
    </div>

    <!-- ተንሳፋፊ የምዝገባ ቁልፍ (ብዙ ቁጥሮች ሲመረጡ የሚመጣ) -->
    <div class="floating-action" id="floatingBtn" onclick="openMultiModal()">
        🎯 የተመረጡትን ቁጥሮች ምዝገባ ጨርስ (<span id="selectedCount">0</span>)
    </div>

    <script>
        let selectedTicketNumbers = [];
        let bookedTickets = JSON.parse(localStorage.getItem('gashayeBookings')) || {};
        let savedPIN = localStorage.getItem('gashayeAppPIN');

        window.onload = function() {
            if (!savedPIN) {
                document.getElementById('lockTitle').innerText = "አዲስ የፒን ቁጥር ያዘጋጁ";
                document.getElementById('lockSub').innerText = "ደብተሩን ለመቆለፍ አዲስ ሚስጥራዊ ቁጥር ይፍጠሩ";
            }
            loadBookingsFromServer();
        };

        async function loadBookingsFromServer() {
            try {
                const res = await fetch('/api/get-bookings');
                const data = await res.json();
                if(data && data.bookings) {
                    bookedTickets = data.bookings;
                    localStorage.setItem('gashayeBookings', JSON.stringify(bookedTickets));
                }
            } catch(e) {
                console.log("Using local cache");
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
                
                const tInfo = bookedTickets[i];
                if (tInfo) {
                    if (tInfo.status === 'approved') {
                        ticket.classList.add('booked');
                        ticket.innerHTML = `${tInfo.name}<br>${tInfo.phone} <span class="ticket-details">ቁጥር፡ ${i} [ተረጋግጧል]</span>`;
                    } else {
                        ticket.classList.add('pending');
                        ticket.innerHTML = `${tInfo.name}<br>እየጠበቀ ነው <span class="ticket-details">ቁጥር፡ ${i} [Pending]</span>`;
                    }
                } else {
                    if (selectedTicketNumbers.includes(i)) {
                        ticket.classList.add('selected');
                        ticket.innerHTML = `ቁጥር ${i} <span class="ticket-details">ተመርጧል ✓</span>`;
                    } else {
                        ticket.innerHTML = `ቁጥር ${i} <span class="ticket-details">ክፍት ነው</span>`;
                    }
                    ticket.onclick = () => handleTicketClick(i);
                }
                grid.appendChild(ticket);
            }
            updateFloatingButton();
        }

        function handleTicketClick(ticketNumber) {
            if (bookedTickets[ticketNumber]) {
                alert(`ይህ ቁጥር ቀደም ሲል ተይዟል!`);
                return;
            }
            const index = selectedTicketNumbers.indexOf(ticketNumber);
            if (index > -1) {
                selectedTicketNumbers.splice(index, 1);
            } else {
                selectedTicketNumbers.push(ticketNumber);
            }
            generateTickets();
        }

        function updateFloatingButton() {
            const btn = document.getElementById('floatingBtn');
            const countSpan = document.getElementById('selectedCount');
            if (selectedTicketNumbers.length > 0) {
                countSpan.innerText = selectedTicketNumbers.length;
                btn.style.display = 'block';
            } else {
                btn.style.display = 'none';
            }
        }

        function openMultiModal() {
            if (selectedTicketNumbers.length === 0) return;
            selectedTicketNumbers.sort((a,b) => a-b);
            document.getElementById('selectedTicketsDisplay').value = selectedTicketNumbers.join(', ');
            document.getElementById('modalTitle').innerText = `የተመረጡ ቁጥሮች (${selectedTicketNumbers.length}) ምዝገባ`;
            document.getElementById('userName').value = '';
            document.getElementById('userPhone').value = '';
            document.getElementById('bookingModal').style.display = 'flex';
        }

        function closeModal() {
            document.getElementById('bookingModal').style.display = 'none';
        }

        async function submitUserBooking() {
            const name = document.getElementById('userName').value.trim();
            const phone = document.getElementById('userPhone').value.trim();
            const pay = document.getElementById('payStatus').value;
            const fileInput = document.getElementById('paymentScreenshot');

            if (!name || !phone) {
                alert('እባክዎ ሙሉ ስምዎን እና ስልክ ቁጥርዎን ያስገቡ!');
                return;
            }

            let screenshotName = fileInput.files.length > 0 ? fileInput.files[0].name : "ስክሪንሾት የለም";

            try {
                const response = await fetch('/api/save-booking', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        tickets: selectedTicketNumbers,
                        name: name,
                        phone: phone,
                        pay_status: pay,
                        screenshot: screenshotName
                    })
                });
                const result = await response.json();
                if(result.status === 'success') {
                    alert('ምዝገባዎ በአግባቡ ተልኳል! አድሚኑ አረጋግጦ እስኪፈቅድ (Approve እስኪያደርግ) በቅርብ ይጠብቁ።');
                    selectedTicketNumbers = [];
                    closeModal();
                    loadBookingsFromServer();
                } else {
                    alert('ስህተት ተፈጥሯል: ' + result.message);
                }
            } catch (err) {
                alert('የኔትወርክ ስህተት ተፈጥሯል!');
            }
        }

        async function payWithChapa() {
            const name = document.getElementById('userName').value.trim();
            const phone = document.getElementById('userPhone').value.trim();
            if (!name || !phone) {
                alert('እባክዎ ከመክፈልዎ በፊት ስምዎን እና ስልክ ቁጥርዎን ያስገቡ!');
                return;
            }
            try {
                const res = await fetch('/api/chapa-pay', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        tickets: selectedTicketNumbers,
                        name: name,
                        phone: phone
                    })
                });
                const data = await res.json();
                if (data.checkout_url) {
                    window.location.href = data.checkout_url;
                } else {
                    alert('የቻፓ ክፍያ ማገናኛ መፍጠር አልተቻለም: ' + (data.message || ''));
                }
            } catch(e) {
                alert('የቻፓ ክፍያ ስህተት ተፈጥሯል');
            }
        }
    </script>
</body>
</html>
