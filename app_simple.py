"""
LINE 老師提醒系統 - 簡化多帳號版本
"""

import os
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from apscheduler.schedulers.background import BackgroundScheduler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LINE Channel 資訊
CHANNEL_1_ACCESS_TOKEN = "oDuJRb/q7oBHUobgLQC/i7/Pg/6Z6EME4/Z7W2h1OrtH0+DAxmsLBeSyvHHn1SViyEe5rHJZqg2o7ZP3RnK/V0aw/uBISldppxPf0GqzUAWGDMPN62nfwfdjBCj0ZG/71uQpqJVQXJ9JYSr0JF0ZQQdB04t89/1O/w1cDnyilFU="
CHANNEL_1_SECRET = "cb58ea355a8c2a01259cd1dc33704264"
CHANNEL_2_ACCESS_TOKEN = "OvwM4sNCR0rVtI8e4EdBeqHLIxAKHg6CiPef66s/g9ONcTRujuGGp5UnUtrLSwvuGjRPxGZiadZfiBL9juCO8IpiK99RAD5NmzCs6pCNt+b+XL1z0JubWAkDnZE++81JOPSSRpxYoZ+p0bdg8p8HXwdB04t89/1O/w1cDnyilFU="
CHANNEL_2_SECRET = "5aba0d7769b5e4468ac1855e78f4e5c8"

app = Flask(__name__)

line_bot_api_1 = LineBotApi(CHANNEL_1_ACCESS_TOKEN)
handler_1 = WebhookHandler(CHANNEL_1_SECRET)
line_bot_api_2 = LineBotApi(CHANNEL_2_ACCESS_TOKEN)
handler_2 = WebhookHandler(CHANNEL_2_SECRET)

DB_PATH = "teacher_system.db"
DAYS_OF_WEEK = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]

def init_db():
    """初始化資料庫"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER NOT NULL,
        user_id TEXT NOT NULL,
        display_name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(account_id, user_id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS schedule (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER NOT NULL,
        day_of_week TEXT NOT NULL,
        teacher_id INTEGER NOT NULL,
        FOREIGN KEY (teacher_id) REFERENCES teachers(id),
        UNIQUE(account_id, day_of_week, teacher_id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER NOT NULL,
        key TEXT NOT NULL,
        value TEXT NOT NULL,
        UNIQUE(account_id, key)
    )''')
    
    for account_id in [1, 2]:
        try:
            c.execute('INSERT INTO settings (account_id, key, value) VALUES (?, ?, ?)',
                      (account_id, 'reminder_message', '{name} 老師您好，提醒您今天下午有課，請您提前做好準備。'))
        except:
            pass
    
    conn.commit()
    conn.close()
    logger.info("資料庫初始化完成")

def add_teacher(account_id, user_id, display_name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO teachers (account_id, user_id, display_name) VALUES (?, ?, ?)',
                  (account_id, user_id, display_name))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

def get_all_teachers(account_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, user_id, display_name FROM teachers WHERE account_id = ? ORDER BY created_at DESC',
              (account_id,))
    results = c.fetchall()
    conn.close()
    return results

def get_schedule(account_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''SELECT s.day_of_week, t.id, t.display_name 
                 FROM schedule s JOIN teachers t ON s.teacher_id = t.id 
                 WHERE s.account_id = ? ORDER BY s.day_of_week''', (account_id,))
    results = c.fetchall()
    conn.close()
    
    schedule_dict = {}
    for day, teacher_id, teacher_name in results:
        if day not in schedule_dict:
            schedule_dict[day] = []
        schedule_dict[day].append({'id': teacher_id, 'name': teacher_name})
    
    return schedule_dict

def add_schedule(account_id, day_of_week, teacher_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO schedule (account_id, day_of_week, teacher_id) VALUES (?, ?, ?)',
                  (account_id, day_of_week, teacher_id))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

def delete_schedule(account_id, day_of_week, teacher_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM schedule WHERE account_id = ? AND day_of_week = ? AND teacher_id = ?',
              (account_id, day_of_week, teacher_id))
    conn.commit()
    conn.close()

def get_setting(account_id, key):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT value FROM settings WHERE account_id = ? AND key = ?', (account_id, key))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def set_setting(account_id, key, value):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO settings (account_id, key, value) VALUES (?, ?, ?)',
              (account_id, key, value))
    conn.commit()
    conn.close()

# Webhook 路由
@app.route("/callback/account1", methods=['GET', 'POST'])
def callback_account1():
    if request.method == 'GET':
        # LINE 驗證 Webhook URL
        logger.info("帳號 1 - Webhook 驗證請求")
        return 'OK', 200
    
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    
    try:
        handler_1.handle(body, signature)
    except InvalidSignatureError:
        return 'Invalid signature', 400
    except Exception as e:
        logger.error(f"Error: {e}")
        return 'Error', 500
    
    return 'OK', 200

@app.route("/callback/account2", methods=['GET', 'POST'])
def callback_account2():
    if request.method == 'GET':
        # LINE 驗證 Webhook URL
        logger.info("帳號 2 - Webhook 驗證請求")
        return 'OK', 200
    
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    
    try:
        handler_2.handle(body, signature)
    except InvalidSignatureError:
        return 'Invalid signature', 400
    except Exception as e:
        logger.error(f"Error: {e}")
        return 'Error', 500
    
    return 'OK', 200

# 訊息處理
@handler_1.add(MessageEvent, message=TextMessage)
def handle_message_account1(event):
    user_id = event.source.user_id
    display_name = "使用者"
    
    try:
        profile = line_bot_api_1.get_profile(user_id)
        display_name = profile.display_name
    except:
        pass
    
    logger.info(f"帳號 1 - 收到訊息: {user_id} ({display_name})")
    add_teacher(1, user_id, display_name)

@handler_2.add(MessageEvent, message=TextMessage)
def handle_message_account2(event):
    user_id = event.source.user_id
    display_name = "使用者"
    
    try:
        profile = line_bot_api_2.get_profile(user_id)
        display_name = profile.display_name
    except:
        pass
    
    logger.info(f"帳號 2 - 收到訊息: {user_id} ({display_name})")
    add_teacher(2, user_id, display_name)

def send_daily_reminder():
    """為兩個帳號發送每日提醒"""
    logger.info("=== 開始每日提醒任務 ===")
    
    today_index = datetime.now().weekday()
    today_name = DAYS_OF_WEEK[today_index]
    
    logger.info(f"今天: {today_name}")
    
    for account_id in [1, 2]:
        logger.info(f"--- 帳號 {account_id} 提醒 ---")
        
        schedule = get_schedule(account_id)
        teachers_today = schedule.get(today_name, [])
        
        if not teachers_today:
            logger.info(f"帳號 {account_id} 今天沒有需要提醒的老師")
            continue
        
        message_template = get_setting(account_id, 'reminder_message')
        if not message_template:
            message_template = "{name} 老師您好，提醒您今天下午有課，請您提前做好準備。"
        
        line_bot_api = line_bot_api_1 if account_id == 1 else line_bot_api_2
        
        for teacher in teachers_today:
            teacher_name = teacher['name']
            
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('SELECT user_id FROM teachers WHERE id = ?', (teacher['id'],))
            result = c.fetchone()
            conn.close()
            
            if result:
                user_id = result[0]
                message = message_template.replace('{name}', teacher_name)
                try:
                    line_bot_api.push_message(user_id, TextSendMessage(text=message))
                    logger.info(f"帳號 {account_id} - 成功向 {teacher_name} 發送提醒")
                except Exception as e:
                    logger.error(f"帳號 {account_id} - 向 {teacher_name} 發送提醒失敗: {e}")

@app.route("/", methods=['GET'])
def index():
    account_id = request.args.get('account', 1, type=int)
    
    teachers = get_all_teachers(account_id)
    schedule = get_schedule(account_id)
    reminder_message = get_setting(account_id, 'reminder_message') or ''
    
    teachers_html = '<p>還沒有老師記錄</p>'
    if teachers:
        teachers_html = ''
        for teacher in teachers:
            teachers_html += f'''
            <div style="background: #f0f0f0; padding: 15px; margin: 10px 0; border-radius: 4px; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h4 style="margin: 0 0 5px 0;">{teacher[2]}</h4>
                    <code style="background: #e8f4f8; padding: 4px 8px; border-radius: 3px; font-size: 12px;">{teacher[1]}</code>
                </div>
            </div>
            '''
    
    schedule_html = '<p>還沒有排課記錄</p>'
    if schedule:
        schedule_html = ''
        for day, teachers_list in schedule.items():
            for t in teachers_list:
                schedule_html += f'''
                <div style="background: #f0f0f0; padding: 10px; margin: 5px 0; border-radius: 4px; display: flex; justify-content: space-between; align-items: center;">
                    <span><strong>{day}</strong> - {t["name"]}</span>
                    <button onclick="deleteSchedule({t['id']}, '{day}')" style="background: #d32f2f; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer;">刪除</button>
                </div>
                '''
    
    html = f'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LINE 老師提醒系統</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #0F4C75 0%, #3282B8 100%); color: white; padding: 30px; text-align: center; }}
        .header h1 {{ font-size: 28px; margin-bottom: 10px; }}
        .content {{ padding: 30px; }}
        .account-selector {{ background: #e8f4f8; padding: 15px; border-radius: 4px; margin-bottom: 30px; }}
        .account-selector label {{ font-weight: 600; margin-right: 10px; }}
        .account-selector select {{ padding: 8px; border: 1px solid #ddd; border-radius: 4px; }}
        .section {{ margin-bottom: 40px; }}
        .section h2 {{ font-size: 18px; font-weight: 600; color: #1a1a2e; margin-bottom: 20px; border-bottom: 2px solid #0F4C75; padding-bottom: 10px; }}
        .form-group {{ margin-bottom: 15px; }}
        .form-group label {{ display: block; margin-bottom: 5px; font-weight: 600; }}
        .form-group input, .form-group select, .form-group textarea {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }}
        .form-group textarea {{ resize: vertical; min-height: 80px; }}
        .btn {{ background: #0F4C75; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-weight: 600; }}
        .btn:hover {{ background: #3282B8; }}
        .btn-small {{ padding: 6px 12px; font-size: 12px; }}
        .form-row {{ display: grid; grid-template-columns: 1fr 1fr auto; gap: 10px; align-items: flex-end; }}
        @media (max-width: 600px) {{
            .form-row {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 LINE 老師提醒系統</h1>
            <p>多帳號課程提醒管理</p>
        </div>
        
        <div class="content">
            <div class="account-selector">
                <label>選擇帳號：</label>
                <select onchange="switchAccount(this.value)">
                    <option value="1" {'selected' if account_id == 1 else ''}>帳號 1</option>
                    <option value="2" {'selected' if account_id == 2 else ''}>帳號 2</option>
                </select>
            </div>
            
            <div class="section">
                <h2>📋 老師列表</h2>
                {teachers_html}
            </div>
            
            <div class="section">
                <h2>📅 新增排課</h2>
                <form id="addScheduleForm">
                    <div class="form-row">
                        <div class="form-group" style="margin-bottom: 0;">
                            <label>選擇老師</label>
                            <select id="teacherSelect" required>
                                <option value="">-- 請選擇老師 --</option>
                                {''.join([f'<option value="{t[0]}">{t[2]}</option>' for t in teachers])}
                            </select>
                        </div>
                        <div class="form-group" style="margin-bottom: 0;">
                            <label>選擇星期</label>
                            <select id="daySelect" required>
                                <option value="">-- 請選擇星期 --</option>
                                {''.join([f'<option value="{day}">{day}</option>' for day in DAYS_OF_WEEK])}
                            </select>
                        </div>
                        <button type="submit" class="btn btn-small">新增</button>
                    </div>
                </form>
            </div>
            
            <div class="section">
                <h2>📅 當前排課表</h2>
                {schedule_html}
            </div>
            
            <div class="section">
                <h2>💬 提醒訊息設定</h2>
                <p style="color: #666; margin-bottom: 15px;">使用 {{name}} 作為老師名稱的佔位符。</p>
                <form id="reminderForm">
                    <div class="form-group">
                        <label>提醒訊息內容</label>
                        <textarea id="reminderMessage" required>{reminder_message}</textarea>
                    </div>
                    <button type="submit" class="btn">保存設定</button>
                </form>
            </div>
            
            <div class="section">
                <h2>⚡ 手動操作</h2>
                <button class="btn" onclick="triggerReminder()">立即發送今日提醒</button>
            </div>
        </div>
    </div>
    
    <script>
        const currentAccount = {account_id};
        
        function switchAccount(accountId) {{
            window.location.href = '/?account=' + accountId;
        }}
        
        document.getElementById('addScheduleForm').addEventListener('submit', async (e) => {{
            e.preventDefault();
            const teacherId = document.getElementById('teacherSelect').value;
            const day = document.getElementById('daySelect').value;
            
            if (!teacherId || !day) {{
                alert('請選擇老師和星期');
                return;
            }}
            
            try {{
                const response = await fetch('/api/schedule/add', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{
                        account_id: currentAccount,
                        teacher_id: parseInt(teacherId),
                        day_of_week: day
                    }})
                }});
                
                const data = await response.json();
                if (data.success) {{
                    alert('排課新增成功');
                    location.reload();
                }} else {{
                    alert('新增失敗: ' + data.message);
                }}
            }} catch (error) {{
                alert('錯誤: ' + error);
            }}
        }});
        
        function deleteSchedule(teacherId, day) {{
            if (!confirm('確定要刪除此排課嗎？')) return;
            
            fetch('/api/schedule/delete', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{
                    account_id: currentAccount,
                    teacher_id: teacherId,
                    day_of_week: day
                }})
            }}).then(r => r.json()).then(data => {{
                if (data.success) {{
                    alert('刪除成功');
                    location.reload();
                }} else {{
                    alert('刪除失敗');
                }}
            }});
        }}
        
        document.getElementById('reminderForm').addEventListener('submit', async (e) => {{
            e.preventDefault();
            const message = document.getElementById('reminderMessage').value;
            
            try {{
                const response = await fetch('/api/settings/reminder', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{
                        account_id: currentAccount,
                        message: message
                    }})
                }});
                
                const data = await response.json();
                if (data.success) {{
                    alert('設定已保存');
                }} else {{
                    alert('保存失敗');
                }}
            }} catch (error) {{
                alert('錯誤: ' + error);
            }}
        }});
        
        function triggerReminder() {{
            if (!confirm('確定要立即發送今日提醒嗎？')) return;
            
            fetch('/api/reminder/trigger', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{account_id: currentAccount}})
            }})
                .then(r => r.json())
                .then(data => alert(data.message))
                .catch(e => alert('錯誤: ' + e));
        }}
    </script>
</body>
</html>'''
    
    return html

@app.route("/api/schedule/add", methods=['POST'])
def api_add_schedule():
    data = request.json
    account_id = data.get('account_id')
    teacher_id = data.get('teacher_id')
    day_of_week = data.get('day_of_week')
    
    if not account_id or not teacher_id or not day_of_week:
        return jsonify({'success': False, 'message': '參數不完整'})
    
    success = add_schedule(account_id, day_of_week, teacher_id)
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': '此排課已存在'})

@app.route("/api/schedule/delete", methods=['POST'])
def api_delete_schedule():
    data = request.json
    account_id = data.get('account_id')
    teacher_id = data.get('teacher_id')
    day_of_week = data.get('day_of_week')
    
    delete_schedule(account_id, day_of_week, teacher_id)
    return jsonify({'success': True})

@app.route("/api/settings/reminder", methods=['POST'])
def api_set_reminder():
    data = request.json
    account_id = data.get('account_id')
    message = data.get('message')
    
    if not message:
        return jsonify({'success': False, 'message': '訊息不能為空'})
    
    set_setting(account_id, 'reminder_message', message)
    return jsonify({'success': True})

@app.route("/api/reminder/trigger", methods=['POST'])
def api_trigger_reminder():
    try:
        send_daily_reminder()
        return jsonify({'success': True, 'message': '提醒已發送'})
    except Exception as e:
        logger.error(f"觸發提醒失敗: {e}")
        return jsonify({'success': False, 'message': f'發送失敗: {e}'})

def setup_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_daily_reminder, 'cron', hour=8, minute=0)
    scheduler.start()
    logger.info("排程器已啟動，每天早上 8:00 發送提醒")

if __name__ == "__main__":
    init_db()
    setup_scheduler()
    app.run(host='0.0.0.0', port=8080, debug=False)
