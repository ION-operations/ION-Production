const API_KEY = 'AIzaSyA9S1wxLNlvpx5g8A9UVS_TIJJVzngV_xY';
const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${API_KEY}`;

const body = {
    contents: [{
        parts: [{
            text: 'JOC connectivity test from Claude Opus 4.6 via AIM-OS. Reply ONLY with JSON: {"status":"connected","provider":"Gemini","model":"your-model-name","message":"brief greeting to the JOC team"}'
        }]
    }],
    generationConfig: { maxOutputTokens: 100, temperature: 0.1 }
};

console.log('Sending test message to Gemini API...');

try {
    const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    });

    if (!res.ok) {
        console.log('HTTP Error:', res.status, await res.text());
        process.exit(1);
    }

    const data = await res.json();
    const text = data.candidates?.[0]?.content?.parts?.[0]?.text || 'No response';
    console.log('');
    console.log('=== GEMINI RESPONSE ===');
    console.log(text);
    console.log('=======================');
    console.log('');
    console.log('CONNECTIVITY TEST: PASS');
} catch (err) {
    console.log('ERROR:', err.message);
    process.exit(1);
}
