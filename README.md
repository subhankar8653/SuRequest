# Suhani Join Request Acceptor Bot

**A Join Request Acceptor Bot that can accept both pending and new join requests with login feature.**

**Powered By [@SuhaniBots](https://t.me/SuhaniBots)**


## Environment Variables

| Variable | Description |
|---|---|
| `API_ID` | Get from [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | Get from [my.telegram.org](https://my.telegram.org) |
| `BOT_TOKEN` | Get from [@BotFather](https://t.me/BotFather) |
| `DB_URI` | MongoDB connection URI |
| `DB_NAME` | MongoDB database name (default: `suhani_joinbot`) |
| `ADMINS` | Your Telegram user ID (for /broadcast) |
| `LOG_CHANNEL` | Log channel ID (starts with -100) |
| `NEW_REQ_MODE` | Set `True` to auto-accept new join requests |

---

## Commands

| Command | Description |
|---|---|
| `/start` | Check bot status |
| `/accept` | Accept all pending join requests |
| `/login` | Login your Telegram account |
| `/logout` | Logout your Telegram account |
| `/broadcast` | Broadcast a message to all users (admin only) |

---

**Powered By [@SuhaniBots](https://t.me/SuhaniBots)**
