const express = require('express');
const axios = require('axios');
const cors = require('cors');
const app = express();

app.use(express.json());
app.use(cors());

// ከ Render Environment Variables የሚወስደው (ካልተገኘ በናሙና የተሰጠውን ይጠቀማል)
const CHASECK = process.env.CHAPA_SECRET_KEY || "CHASECK-SncZN81Mx80yQcPiXJwRXDF6MdgchtNV";

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
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
