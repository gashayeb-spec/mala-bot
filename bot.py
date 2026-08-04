<!DOCTYPE html>
<html lang="am">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mala Mini App</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body {
            background-color: #0f1016;
            color: #ffffff;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 0;
            padding-bottom: 70px;
        }
        .container {
            padding: 16px;
        }
        .header {
            text-align: center;
            margin-bottom: 20px;
        }
        .card {
            background-color: #171923;
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 16px;
            border: 1px solid #2d3748;
        }
        .wallet-balance {
            font-size: 32px;
            font-weight: bold;
            color: #63b3ed;
            text-align: center;
            margin: 10px 0;
        }
        .btn-primary {
            background-color: #3182ce;
            color: white;
            border: none;
            width: 100%;
            padding: 12px;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 10px;
        }
        .nav-bar {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: #12141c;
            display: flex;
            justify-content: space-around;
            padding: 10px 0;
            border-top: 1px solid #2d3748;
        }
        .nav-item {
            text-align: center;
            color: #a0aec0;
            font-size: 12px;
            text-decoration: none;
            cursor: pointer;
        }
        .nav-item.active {
            color: #ffffff;
        }
    </style>
</head>
<body>

    <div class="container">
        <div class="header">
            <h2>Mala</h2>
            <p style="color: #a0aec0; font-size: 14px;">Social growth & premium services</p>
        </div>

        <div class="card">
            <h3 style="margin: 0; text-align: center; color: #a0aec0;">Wallet</h3>
            <div class="wallet-balance">0.00 ETB</div>
            <div style="display: flex; gap: 10px;">
                <button class="btn-primary" style="background-color: #2b6cb0;">Deposit</button>
                <button class="btn-primary" style="background-color: #2d3748;">Withdraw</button>
            </div>
        </div>

        <div class="card" onclick="alert('Social Media Services clicked!')" style="cursor: pointer;">
            <h3>Social Media</h3>
            <p style="color: #a0aec0; font-size: 13px;">Grow followers, likes, and views.</p>
        </div>
    </div>

    <div class="nav-bar">
        <div class="nav-item active">👤 መግቢያ</div>
        <div class="nav-item">📋 ትዕዛዞች</div>
        <div class="nav-item">🌐 ሪፈራል</div>
        <div class="nav-item">📖 መመሪያ</div>
        <div class="nav-item">💳 ዋሌት</div>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
    </script>
</body>
</html>
