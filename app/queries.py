from datetime import date
from storage import read_tasks, update_tasks
from config import SOFT_DELETE

# -------------------- HElPERS ----------------------------------------------------
def _is_active(t):
    return not t.get("is_deleted", False)

def _today():
    return str(date.today())

def get_max_id():
    tasks = read_tasks()
    return max((t['id'] for t in tasks), default=0)

def get_all_active_chat_ids():
    tasks = read_tasks()
    return list({t['chat_id'] for t in tasks if _is_active(t)})

# -------------------- GET DATA ----------------------------------------------------
def get_today_pending_tasks(chat_id:int):
    tasks = read_tasks()
    today = _today()
    return [t for t in tasks if t['chat_id'] == chat_id and t['date'] == today and not t["done"] and _is_active(t)]

def get_today_tasks(chat_id:int):
    tasks = read_tasks()
    today = _today()
    return [t for t in tasks if t['chat_id'] == chat_id and t['date'] == today and _is_active(t)]

def get_today_done_tasks(chat_id:int):
    tasks = read_tasks()
    today = _today()
    return [t for t in tasks if t['chat_id'] == chat_id and t['date'] == today and t["done"] and _is_active(t)]

# -------------------- UPDATE DATA ----------------------------------------------------
def store_task(task):
    
    try:
        def _add(tasks):
            tasks.append(task)
            return tasks
        
        update_tasks(_add)
        return {  'ok': True, 'affected': 1,  'reason': None }
        
    except Exception as e :
        return { 'ok': False, 'affected': 0, 'reason': str(e) or "Unknown error occurred"  }
        
def remove_task_by_id(task_id: int, chat_id: int):
    affected = 0
    try: 
        def _remove(tasks):
            nonlocal affected
            if SOFT_DELETE:
                for t in tasks:
                    if t["id"] == task_id and t["chat_id"] == chat_id and _is_active(t):
                        t['is_deleted'] = True
                        affected = 1
                        break
            else:
                ori_len = len(tasks)
                tasks[:] = [t for t in tasks if not (t["id"] == task_id and t["chat_id"] == chat_id)]
                affected = ori_len - len(tasks)
            return tasks
            
        update_tasks(_remove)
        
        if affected == 0:
            return {'ok': False, 'affected':affected, 'reason': "Id not found" }

            
        return {'ok': True, 'affected':affected, 'reason': None }
        
    except Exception as e:
        return { 'ok': False, 'affected':0, 'reason': str(e) or "Unknown error occurred"}
    
def remove_today_tasks(chat_id:int):
    
    affected = 0
    today = _today()

    try:
        
        def _remove(tasks):
            nonlocal affected
            if SOFT_DELETE:
                for t in tasks:
                    if t["chat_id"] == chat_id  and t['date']== today and _is_active(t):
                        t['is_deleted'] = True
                        affected += 1
            else:
                ori_len = len(tasks)
                tasks[:] = [t for t in tasks if not (t["chat_id"] ==  chat_id and t['date'] == today and _is_active(t))]
                affected = ori_len - len(tasks)
            return tasks
            
        update_tasks(_remove)
        
            
        return {'ok': True, 'affected':affected, 'reason': None }
    except Exception as e:
        return { 'ok': False, 'affected':0, 'reason': str(e) or "Unknown error occurred"}

def remove_all_tasks(chat_id:int):
    affected = 0
    try:
        def _remove(tasks):
            nonlocal affected 
            if SOFT_DELETE:
                for t in tasks:
                    if t["chat_id"] == chat_id and _is_active(t):
                        t['is_deleted'] = True
                        affected += 1
            else:
                ori_len = len(tasks)
                tasks[:] = [t for t in tasks if t["chat_id"] != chat_id]
                affected = ori_len - len(tasks)
            return tasks
        
        update_tasks(_remove) 
        return {'ok': True, 'affected':affected, 'reason': None}
        
    except Exception as e:
        return { 'ok': False, 'affected':0, 'reason': str(e) or "Unknown error occurred"}

def remove_done_tasks(chat_id: int):
    affected = 0
    try:
        def _remove(tasks):
            nonlocal affected
            if SOFT_DELETE:
                for t in tasks:
                    if t['chat_id']== chat_id and t['done'] and _is_active(t):
                        t['is_deleted'] = True
                        affected += 1
            else:
                ori_len = len(tasks)
                tasks[:] = [t for t in tasks if t['chat_id'] == chat_id and not t['done']]
                affected = ori_len - len(tasks)
            return tasks

        update_tasks(_remove) 
        return {'ok': True, 'affected':affected, 'reason': None}
    
    except Exception as e:
        return {
            'ok': False,
            'affected':0,
            'reason': str(e) or "Unknown error occurred" 
        }

def mark_as_done(task_id: int, chat_id: int):
    found = 0
    try:
        def _mark(tasks):
            nonlocal found
            for t in tasks:
                if t['id'] == task_id and t['chat_id'] == chat_id:
                    t['done'] = True
                    found = True
                    break
            
            return tasks

        update_tasks(_mark)
        
        if found:
            return {'ok': True, 'affected':1, 'reason': None}
               
        return {'ok': False, 'affected':0, 'reason': 'Id not found'}
            
    except Exception as e:
        return {'ok': False, 'affected':0, 'reason': str(e) or "Unknown error occurred"}