# Taskbot

A personal Telegram bot for managing daily tasks. Sends reminders in the morning, afternoon, and evening if you still have pending stuff. Also seeds a default task list every morning so you don't forget the routine things.

Built for personal use, deployed on fly.io.

---

## commands

| command | what it does |
|---|---|
| `/add <task>` | add a new task |
| `/add_next <task>` | add a new task for the next day|
| `/list` | today's tasks |
| `/list done` | today's completed tasks |
| `/list pending` | today's pending tasks only |
| `/list prev` | all yesterday's tasks|
| `/list prev` | all tomorrow's tasks|
| `/done <id>` | mark a task as done |
| `/clear <id>` | remove a specific task |
| `/clear all` | remove everything |
| `/clear today` | remove today's tasks |
| `/clear done` | remove completed tasks |

---

## running locally

**1. clone and set up**
```bash
git clone <repo>
cd <repo>
pip install -r requirements.txt
```

**2. set your bot token**
```bash
export BOT_TOKEN=your_token_here
```
Don't have a token yet? Talk to [@BotFather](https://t.me/BotFather) on Telegram.

**3. run**
```bash
python app/main.py
```

Tasks are saved to `app/data/tasks.json`. The folder gets created automatically on first run.

---

## deploying to fly.io

**1. install flyctl and login**
```bash
curl -L https://fly.io/install.sh | sh # or https://fly.io/docs/getting-started/launch-demo/#1-install-flyctl
fly auth login
```

**2. create the app**
```bash
fly launch
```

**3. create a persistent volume** (so tasks survive redeploys)
```bash
fly volumes create bot_data --size 1
```

**4. set the bot token**
```bash
fly secrets set BOT_TOKEN=your_token_here
```

**5. deploy**
```bash
fly deploy
```

**fly.toml** — make sure these are in there:
```toml
[env]
  ENV = "production"
  DATA_DIR = "/data"

[mounts]
  source = "bot_data"
  destination = "/data"
```

---

## project structure

```
app/
├── main.py         # entry point, PTB setup
├── handlers.py     # command handler functions
├── commands.py     # command registry
├── queries.py      # all read/write operations
├── storage.py      # file I/O + threading lock
├── scheduler.py    # daily notifications + task seeding
└── config.py       # env vars, paths, scheduler times
```

---

## configuration

Everything worth tweaking is in `config.py`:

**notification times** (Jakarta time by default)
```python
NOTIFY_TIMES = [
    {"hour": 7,  "minute": 0,  "label": "morning"},
    {"hour": 13, "minute": 0,  "label": "afternoon"},
    {"hour": 20, "minute": 0,  "label": "evening"},
]
```

**default daily tasks** — seeded every morning for all known chats
```python
DEFAULT_DAILY_TASKS = [
    "Morning dhikr (Al-Ma'tsurat)",
    "Review today's schedule",
    "Evening dhikr (Al-Ma'tsurat)",
]
```
Set to `[]` to disable auto-seeding.

**timezone**
```python
TIMEZONE = ZoneInfo("Asia/Jakarta")
```

---

## requirements

- Python 3.12+
- `python-telegram-bot[job-queue]`

---

## notes

- Tasks are scoped per `chat_id` — each chat has its own isolated list
- Soft delete is enabled by default; tasks are flagged `is_deleted` rather than removed immediately
