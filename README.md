# Telegram AI Assistant for Accelerate Prosperity

Telegram bot for [@accelerateprosperitybot](https://t.me/accelerateprosperitybot).

Current program: [Starline Accelerator](https://app.notion.com/p/Starline-Accelerator-3873a0c5168e80de8810e8c3c5f5fbf4).

## What works now

- Language: Russian and English only (Telegram TZ). `/start` always shows the picker; menu has **Язык / Language**; free-text language is auto-detected
- Menu sections show published program data without the model
- Free-text questions go to Gemini (`gemini-3.6-flash`) using `app/ai/prompt.md` and the selected program record
- No confirmed source → no answer + handoff to the program coordinator (`@fara_imatshoevna` in the Starline guide)
- Unanswered questions and tickets are stored locally in `data/runtime/` (not in git)
- Reminders while `python run.py` is running

## Run locally (Windows)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Fill secrets in `.env`, then:

```powershell
python run.py
```

Open Telegram and send `/start`.

## Environment variables

Copy `.env.example` to `.env`. Git ignores `.env`. Do not commit tokens.

| Variable | Required | Meaning |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | yes | BotFather token |
| `GEMINI_API_KEY` | yes for AI answers | Google AI Studio key |
| `GEMINI_MODEL` | no | default `gemini-3.6-flash` |
| `COORDINATOR_USERNAME` | no | Telegram username that receives ticket copies in this bot (must have written to the bot once) |
| `BOT_NAME` | no | display name |
| `TIMEZONE` | no | default `Asia/Dushanbe` |

Values in the process environment override `.env`.

## Knowledge

- Organization facts: `app/kb/knowledge.md`
- Programs list: `app/kb/programs.json`
- Starline guide: `app/kb/starline.md`

Restart the bot after editing those files.
