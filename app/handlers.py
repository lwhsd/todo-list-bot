
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import date
from queries import remove_today_tasks, remove_all_tasks, remove_done_tasks, remove_task_by_id, store_task, get_max_id, mark_as_done, get_today_pending_tasks, get_today_tasks, get_today_done_tasks

logger = logging.getLogger(__name__)
TASK_STATUS = {
    "not_started": "⬜",
    "done": "✅",
}

_CLEAR_USAGE = (
        "📝 <b>Usage: /clear</b>\n\n"
        "<code>/clear [id|all|today|done]</code>\n\n"
        "<b>Examples:</b>\n"
        "/clear 1\n"
        "/clear all"
    )

_CLEAR_USAGE = (
        "📝 <b>Usage: /list</b>\n\n"
        "<code>/list OR /list [all|pending|done]</code>\n\n"
        "<b>Examples:</b>\n"
        "/list \n"
        "/list all\n"
        "/list today"
    )

async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Usage: /add <task>")
        return
    
    response = store_task({
        "id": get_max_id() + 1,
        "chat_id": update.effective_chat.id,
        "title": text,
        "date": str(date.today()),
        "done": False,
        "last_notified": None,
        "is_deleted": False
    })
    
    if response["ok"]:
        await update.message.reply_text("Task added ✅")
    else:
        await update.message.reply_text("Failed adding the task")
    

async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id 
    try:
        
        arg = context.args[0].lower() if context.args else None
        
        if arg is None or arg == "all":
            taskList = get_today_tasks(chat_id)
        elif arg == 'done':
            taskList = get_today_done_tasks(chat_id)
        elif arg == 'pending':
            taskList = get_today_pending_tasks(chat_id)
        else:
            raise Exception(f'Invalid param: {arg}')
        
        if not taskList:
            await update.message.reply_text("No requested tasks available")
            return
            
        await update.message.reply_text("\n".join(f"{t['id']}. {TASK_STATUS['done'] if t['done'] else TASK_STATUS['not_started']} {t['title']}" for t in taskList))
    except Exception as e:
        await update.message.reply_text(_CLEAR_USAGE , parse_mode='HTML')
        

async def done_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        task_id = int(context.args[0])
    except Exception:
        await update.message.reply_text("Usage: /done <id>")
        return

    chat_id = update.effective_chat.id 
    response = mark_as_done(task_id, chat_id)
    if 'ok' in response and response['ok']:
         await update.message.reply_text(f"Task: {task_id} is marked as done")
         return

    await update.message.reply_text("Task not found")
    
async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    try:
        arg = context.args[0]
    except IndexError:
        await update.message.reply_text(_CLEAR_USAGE, parse_mode="HTML")
        return

    if not arg.isdigit() and arg.lower() not in ("all", "today", "done"):
        await update.message.reply_text(_CLEAR_USAGE, parse_mode="HTML")
        return

    keyboard = [[
        InlineKeyboardButton("Yes, proceed", callback_data=f"clear_confirm;{arg}"),
        InlineKeyboardButton("No, cancel", callback_data=f"clear_cancel;{arg}"),
    ]]
    await update.message.reply_text(
        "This action will remove your task(s). Are you sure?",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    
async def clear_confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    query = update.callback_query
    chat_id = update.effective_chat.id 
    try:
    
        action , arg = query.data.split(";") 
        if action == "clear_cancel":
            await query.edit_message_text(text="Action cancelled.")
            return
        
        if arg.isdigit():
            task_id = int(arg)
            response = remove_task_by_id(task_id, chat_id)
            if 'ok' in response and response['ok']:
                await query.edit_message_text(text=f"Task {arg} removed.")
            else:
                await query.edit_message_text(text=f"Task {arg} not found")
            return
        
        
        dispatch = {
            'all' : (remove_all_tasks, "All tasks cleared."),
            'today' : (remove_today_tasks, "Today's tasks cleared."),
            'done':  (remove_done_tasks,   "Done tasks cleared."),
        }
            
        fn , ok_msg = dispatch.get(arg.lower(), (None, None))  
        if fn is None:
            await query.edit_message_text(_CLEAR_USAGE, parse_mode="HTML")
            return
        
        response = fn(chat_id)
        if 'ok' in response and response['ok']:
             await query.edit_message_text(ok_msg)
        else:
            await query.edit_message_text(f"Failed: {response.get('reason', 'unknown error')}")
            
    except Exception as e :
        logger.error("Exception while handling delete confirmation :\n%s", e)
        await query.edit_message_text(_CLEAR_USAGE , parse_mode='HTML')
        