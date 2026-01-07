from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime, date
from typing import List, Dict, Optional
from pathlib import Path

app = Flask(__name__)

CONFIG_DIR = Path.home() / ".career_todo"
DATA_FILE = str(CONFIG_DIR / "todos.json")

CATEGORIES = ["자소서", "포폴", "면접", "기업분석", "AI활용", "기타"]
PRIORITIES = ["상", "중", "하"]

def today_str() -> str:
    return date.today().isoformat()

def parse_date(s: str) -> Optional[str]:
    s = s.strip()
    if not s:
        return None
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return s
    except ValueError:
        return None

def ensure_data_dir():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def load_todos() -> List[Dict]:
    ensure_data_dir()
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []

def save_todos(todos: List[Dict]) -> None:
    ensure_data_dir()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)

def next_id(todos: List[Dict]) -> int:
    if not todos:
        return 1
    return max(t.get("id", 0) for t in todos) + 1

@app.route('/')
def index():
    todos = load_todos()
    return render_template('index.html', todos=todos, categories=CATEGORIES, priorities=PRIORITIES)

@app.route('/add', methods=['POST'])
def add():
    todos = load_todos()
    title = request.form.get('title')
    category = request.form.get('category')
    priority = request.form.get('priority')
    due_date = parse_date(request.form.get('due_date', ''))

    if title:
        todo = {
            "id": next_id(todos),
            "title": title,
            "category": category,
            "priority": priority,
            "due_date": due_date,
            "done": False,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "updated_at": None,
            "notes": ""
        }
        todos.append(todo)
        save_todos(todos)
    return redirect(url_for('index'))

@app.route('/toggle/<int:todo_id>')
def toggle(todo_id):
    todos = load_todos()
    for t in todos:
        if t['id'] == todo_id:
            t['done'] = not t['done']
            t['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            break
    save_todos(todos)
    return redirect(url_for('index'))

@app.route('/delete/<int:todo_id>')
def delete(todo_id):
    todos = load_todos()
    todos = [t for t in todos if t['id'] != todo_id]
    save_todos(todos)
    return redirect(url_for('index'))

@app.route('/progress')
def progress():
    todos = load_todos()
    if not todos:
        return "0"
    done = sum(1 for t in todos if t.get("done"))
    pct = round((done / len(todos)) * 100, 1)
    return f"{pct}%"

if __name__ == '__main__':
    app.run(debug=True)