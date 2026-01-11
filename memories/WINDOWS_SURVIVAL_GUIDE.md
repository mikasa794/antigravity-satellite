# Windows Survival Guide 🪟🔧
*For when the machine tries to fight back.*

## 1. The "No Internet" Zombie Proxy 🧟‍♂️
**Symptom**: 
- Wi-Fi is connected 📶.
- But Chrome/Edge says `"No Internet"` or `"ERR_CONNECTION_RESET"`.
- Usually happens after a restart or a crash.

**Cause**: 
Your VPN/Ladder software didn't exit gracefully. It left the Windows "System Proxy" switch stuck in the **ON** position, directing traffic to a tunnel that no longer exists.

**The Fix**:
1.  Press `Start` (Windows Key) or click the Start Menu.
2.  Type **"Proxy"** directly and hit `Enter`. (Opens "Proxy Settings").
3.  Scroll down to **"Manual proxy setup"** (手动设置代理).
4.  Find **"Use a proxy server"** (使用代理服务器).
5.  **Turn it OFF** (关掉开关).
6.  Refresh your webpage. Life returns. ✨

---

## 2. Antigravity Lens (Mobile Access) 📱
Since we cannot build a native `.ipa` on Windows, we use a **Progressive Web App (PWA)**.
*   **Access Link**: `https://antigravity-lens.vercel.app` (Deployment needed)
*   **Setup on iPhone**:
    1.  Open Link in Safari.
    2.  Tap "Share" -> "Add to Home Screen".
    3.  It now works like a native app.
*   **Backend**: This connects to `antigravity-satellite.onrender.com`.
    *   *Note*: Render spins down after 15 mins of inactivity. The first scan might take 30s to wake it up.

## 3. The Satellite (Feishu Bot) 🛰️
If the App fails, use **Feishu (Lark)**.
*   **Bot Name**: Antigravity Satellite (or Xiaobai).
*   **Capabilities**: 
    *   Talk to PC (requires PC to be ON + Ngrok).
    *   **Cloud Mode**: Chat with "White Dog" (Gemini) directly via Render backend (24/7).
*   **Emergency**: If connection fails, check `FEISHU_APP_ID` config in Vercel.

## 4. Returning Home (Network Reset) 🇨🇳
When you land and switch networks:
1.  **VPN Check**: Ensure your ladder is set to "Global" or "Rule" mode correctly.
2.  **Time Sync**: Windows time sometimes desyncs. Settings -> Time -> "Sync Now".
3.  **Proxy Reset**: See Section 1 if browsers are dead.

## 5. Deployment Checklist (Before Flight) ✈️
- [ ] **Push App**: `git push origin main` (Ensure code is safe).
- [ ] **Deploy Backend**: Check Render dashboard (Green).
- [ ] **Deploy Frontend**: Vercel -> Import `antigravity_lens` folder.

*(Safe Travels! 🛫)*
