# JParty! for the web
Live: https://jparty-web.vercel.app

The original Python application is preserved. This React/Vite web recreation uses maintained PeerJS, Papa Parse, QRCode and Cheerio rather than custom networking/parsers.

## Play
Host a game and keep the private host tab open/awake. Open the audience display for a TV. Up to eight players scan the QR or use the 12-character room code. Local players work without phones. Start, select a clue, read it, open buzzers, and judge. Incorrect responses reopen for other players; Daily Doubles do not. Space opens buzzers/returns to board, left/right arrows judge. Scores can be manually set and players removed. Advance through Double and Final; phones privately submit Final wagers and responses.

## Creator
The original 61-clue demo is ready to play. Edit all categories, clues, correct responses, values, Daily Doubles, Final and HTTPS image/audio/video/YouTube URLs. Save on this device, import/export JSON, start blank, or import legacy CSV. Required fields and structure are validated.

Original Google Sheets / JeopardyLabs-extension CSV layout: category rows 1/14, clue rows 2–6/15–19, response rows 8–12/21–25, Final metadata in the last row. Public original Sheet IDs/URLs can be imported. J-Archive accepts IDs/URLs or saved HTML files, supporting current hidden-response and older hover markup. Incomplete games are rejected. Third-party archives can block requests.

## Parity
Retained: JParty! name/blue board; eight online phone buzzers; QR join; private host/public audience; manual scores/removal; negative-answer options; control indicator; early lockout default 500ms; first/early/late/fastest buzz stats; correct/incorrect/revenue/losses; default four-second clue timer; Daily Double wagers bounded by score or $1,000/$2,000; Double Jeopardy; 31-second Final; ties/winner; keyboard judging; skipping; media; results export; local session recovery.

Five visual palettes: default, Christmas, Halloween, EightiesSynthwave, BibleBonkers. Original default audio plus all available Christmas, Halloween, EightiesSynthwave and BibleBonkers soundtrack overrides are included. Host lobby has optional looping intro music; theme changes restart the selected intro, and starting play stops it. Final and timeout audio stop cleanly on completion or manual closure. Added: visual board editor, JSON backups, local persistence and internet connections without Python.

Intentionally omitted: physical buzzers. Category boards reveal in staggered animated columns, honoring prefers-reduced-motion. Statistics award the original Most Correct, Most Wrong, Most Revenue, Quickest Buzzer and Most buzz-ins titles (ties shared; quickest ignores missing times rather than starting at zero). Results export includes awards. Themes are web palettes, not pixel-identical desktop asset reproductions.

## Free realtime architecture and limitations
Vercel Hobby static frontend plus serverless import endpoint. PeerJS 1.5.5 uses its free public PeerServer for signaling and direct WebRTC data channels to the authoritative host browser. This is real network multiplayer, NOT localStorage synchronization. No paid account, card, database or TURN relay.

The free signaling service has no SLA. Some corporate/guest/carrier NAT/firewall networks block direct WebRTC without TURN: try compatible Wi-Fi/hotspot or local manual players. First arrival at the host wins; network latency affects fairness. Trusted party play, not anti-cheat tournaments. Room codes are capability links, not authentication. Host closure/sleep stops the game. Local session recovery creates a new room; remote players must rejoin. Boards and sessions persist on the host device only: export backups. Media depends on source permissions and embed rules. Audio needs a user interaction; audience video playback is not frame-synchronized.

Public projections strip all unrevealed responses, future Daily Doubles, private wagers and Final submissions. Private host access is not encoded in share links. Import endpoint fetches only validated J-Archive numeric IDs and Google Sheets IDs, not arbitrary URLs.

## Develop/test/deploy
Node 22+. From web/: npm ci; npm run dev; npm test; npm run build.
Browser smoke: npx playwright install --with-deps chromium; node tests/browser.mjs.
Set BASE_URL=https://jparty-web.vercel.app to test production. It uses separate host, phone and audience browser contexts and saves screenshots in screenshots/.
Deploy from web/ with vercel deploy --prod. Vercel detects Vite, outputs dist, and serves api/import.js as a serverless function. Never put credentials in the client bundle.

GPL-3.0-only, as the original repository.
