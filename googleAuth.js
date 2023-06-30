const express = require('express');
const { OAuth2Client } = require('google-auth-library');

const router = express.Router();
const client = new OAuth2Client('YOUR_CLIENT_ID');

router.post('/google-auth', async (req, res) => {
  const idToken = req.body.idToken;

  try {
    const ticket = await client.verifyIdToken({
      idToken: idToken,
      audience: 'YOUR_CLIENT_ID',
    });

    const payload = ticket.getPayload();
    const userId = payload.sub;

    // Perform further actions based on the user ID or other data

    res.status(200).json({ message: 'Authentication successful' });
  } catch (error) {
    console.error('Authentication failed:', error);
    res.status(401).json({ error: 'Authentication failed' });
  }
});

module.exports = router;
