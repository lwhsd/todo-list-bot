from telegram.ext import (
    Application,
    ContextTypes
)
from config import NOTIFY_TIMES, TIMEZONE, DEFAULT_DAILY_TASKS
from datetime import datetime, time
from queries import get_today_pending_tasks, get_all_active_chat_ids, get_today_tasks, store_task, get_max_id
import logging

logger = logging.getLogger(__name__)

TASK_STATUS = {
    "not_started": "⬜",
    "done": "✅",
}

HEADER_MSG = {
    'morning' : 'Hi hi, Ready to rock today ???',
    'afternoon' : 'Almost there keep it up !!!',
    'evening' : 'Come on!! Last push for today !!!'
}

def _today_str() -> str:
    return datetime.now(tz=TIMEZONE).strftime("%Y-%m-%d")

def _slot_label(hour):
    for h in NOTIFY_TIMES:
        if h['hour'] == hour:
            return h['label']
    return 'Unknown'

async def _seed_daily(context: ContextTypes.DEFAULT_TYPE):
    
    print('Start seeding daily tasks')
    if not DEFAULT_DAILY_TASKS:
        return
    
    try:
        chat_ids = get_all_active_chat_ids()
        today = _today_str()
        
        for chat_id in chat_ids:
            existing_title = {t['title'] for t in get_today_tasks(chat_id)}
            seeded = 0
            
            for dt in DEFAULT_DAILY_TASKS:
                if dt in existing_title:
                    continue
                
                store_task({
                    "id": get_max_id() + 1,
                    "chat_id":chat_id,
                    "title": dt,
                    "date": today,
                    "done": False,
                    "last_notified": None,
                    "is_deleted": False
                })
                seeded += 1
                logger.info("a %s daily task have been added at %s for chat id %s",  dt, today, chat_id)
    except Exception as e:
        logger.warning('Failed to setup scheduler: %s', e )   

async def _notify_pending(context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    now = datetime.now(tz=TIMEZONE)
    slot_label = _slot_label(now.hour)
    
    chat_ids = get_all_active_chat_ids()
    
    for chat_id in chat_ids:
        
        pending = get_today_pending_tasks(chat_id)
        
        print(f'Today pending tasks: {pending}')
        if not pending:
            continue
        
        print(f'Today pending tasks: {pending}')
        lines = "\n".join(f" {t['id']}. {TASK_STATUS['not_started']} {t["title"]}" for t in pending)
        
        try:
            await bot.send_message(chat_id=chat_id, text=f"{HEADER_MSG[slot_label]} \n\n{lines} \n\nUse /done <id> to mark a task complete")
            
        except Exception as e:
            logger.warning("Failed to notify chat %s at slot %s: %s", chat_id, slot_label, e)


def start_scheduler(app: Application):
    jq = app.job_queue
    try:
        print(f'Start scheduler')
        for t in NOTIFY_TIMES:
            slot_time = time(hour=t["hour"], minute=t["minute"], tzinfo=TIMEZONE)
            
            if t['label'] == 'morning':
                jq.run_daily(
                    _seed_daily,
                    time=slot_time,
                    name=f'seed_daily_at_{_today_str}'
                )
                
            print(f'Slot time: {slot_time}')
            jq.run_daily(
                _notify_pending,
                time=slot_time,
                name=f'notify_pending_{t['label']}'
            )

    except Exception as e:
        logger.error('Failed to setup scheduler: %s', e )