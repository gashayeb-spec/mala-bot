const express = require('express');
const axios = require('axios');
const cors = require('cors');
const path = require('path');
const { Telegraf } = require('telegraf');

const app = express();
app.use(express.json());
app.use(cors());

// እጅግ በጣም አስፈላጊ: ስታቲክ ፋይሎች (HTML, CSS) ያሉበትን ፎልደር ማሳየት
app.use(express.static(__dirname));

const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN || "8543715567:AAG56vVGC2LDpIOED-euwwF72f-245TG27U";
const CHASECK = process.env.CHAPA_SECRET_KEY || "CHASECK-SncZN81Mx80yQcPiXJwRXDF6MdgchtNV";

const bot = new Telegraf(BOT_TOKEN);

bot.start((ctx) => {
    const userId = ctx.from.id;
    const firstName = ctx.from.first_name;

    ctx.reply(`ሰላም ${firstName} 👋 ወደ መላ ቦት እንኳን ደህና መጡ!\n\nየእርስዎ ቴሌግራም አይዲ: ${userId}\n\nአገልግሎቶቹን ለመጠቀም ከታች ያለውን ቁልፍ ይጫኑ፡`, {
        reply_markup: {
            inline_keyboard: [
                [{ text: "🚀 መላ መተግበሪያን ክፈት", web_app: { url: "https://mala-bot.onrender.com" } }]
            ]
        }
    });
});

bot.launch();

// ቀጥታ ወደ index.html እንዲያመራ ማድረግ
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.post('/verify-payment', async (req, res) => {
    const { tx_ref } = req.body;
    try {
        const response = await axios.get(`https://api.chapa.co/v1/transaction/verify/${tx_ref}`, {
            headers: { Authorization: `Bearer ${CHASECK}` }
        });
        if (response.data.status === 'success') {
            return res.json({ status: 'success', message: 'ክፍያው ተሳክቷል!' });
        }
        return res.json({ status: 'failed', message: 'ክፍያው አልተሳካም' });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server and Bot running on port ${PORT}`));
