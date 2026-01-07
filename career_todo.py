#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Career Todo (커리어캐쳐 스타일)
- 비개발자도 실행 가능한 콘솔 Todo 앱
- CRUD(추가/조회/수정/삭제) + 완료 처리 + 필터 + 진행률 + JSON 저장

변경사항:
- 데이터 파일을 실행 폴더가 아닌 사용자 홈의 설정 폴더(~/.career_todo/todos.json)에 저장
- 시작/종료 시 Ctrl+C(KeyboardInterrupt)를 우아하게 처리
"""

import json
import os
from datetime import datetime, date
from typing import List, Dict, Optional
from pathlib import Path

CONFIG_DIR = Path.home() / ".career_todo"
DATA_FILE = str(CONFIG_DIR / "todos.json")

CATEGORIES = ["자소서", "포폴", "면접", "기업분석", "AI활용", "기타"]
PRIORITIES = ["상", "중", "하"]


def today_str() -> str:
    return date.today().isoformat()


def parse_date(s: str) -> Optional[str]:
    """
    날짜 입력(YYYY-MM-DD) 검증.
    - 빈 값이면 None 반환
    - 올바르면 ISO 문자열 반환
    """
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
        # 파일이 깨졌거나 형식이 이상하면 안전하게 빈 목록
        return []


def save_todos(todos: List[Dict]) -> None:
    ensure_data_dir()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)


def next_id(todos: List[Dict]) -> int:
    if not todos:
        return 1
    return max(t.get("id", 0) for t in todos) + 1


def pick_from_list(title: str, options: List[str], default: Optional[str] = None) -> str:
    print(f"\n{title}")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    while True:
        prompt = "번호를 입력하세요"
        if default:
            prompt += f" (Enter=기본값: {default})"
        prompt += ": "

        s = input(prompt).strip()
        if not s and default:
            return default
        if s.isdigit():
            idx = int(s)
            if 1 <= idx <= len(options):
                return options[idx - 1]
        print("❗ 올바른 번호를 입력해 주세요.")


def input_text(prompt: str, default: Optional[str] = None, allow_empty: bool = False) -> str:
    while True:
        s = input(f"{prompt}{f' (Enter=기본값: {default})' if default else ''}: ").strip()
        if not s and default is not None:
            return default
        if allow_empty:
            return s
        if s:
            return s
        print("❗ 입력이 비어있습니다. 다시 입력해 주세요.")


def print_line():
    print("-" * 70)


def format_todo(t: Dict) -> str:
    done = "✅" if t.get("done") else "⬜"
    due = t.get("due_date") or "-"
    pr = t.get("priority") or "-"
    cat = t.get("category") or "-"
    title = t.get("title") or "(제목 없음)"
    created = t.get("created_at", "-")
    return f"{done} [ID:{t.get('id')}] ({cat}/{pr}) 마감:{due} | {title} | 생성:{created}"


def list_todos(todos: List[Dict], mode: str = "all"):
    """
    mode:
      - all: 전체
      - open: 미완료
      - done: 완료
      - today: 오늘 마감
      - week: 이번 주 마감(오늘~7일)
      - category:<name>
    """
    filtered = todos[:]

    if mode == "open":
        filtered = [t for t in filtered if not t.get("done")]
    elif mode == "done":
        filtered = [t for t in filtered if t.get("done")]
    elif mode == "today":
        filtered = [t for t in filtered if (t.get("due_date") == today_str())]
    elif mode == "week":
        # 간단 주간: 오늘부터 7일 이내
        today = datetime.strptime(today_str(), "%Y-%m-%d").date()
        def in_week(due: Optional[str]) -> bool:
            if not due:
                return False
            try:
                d = datetime.strptime(due, "%Y-%m-%d").date()
                return 0 <= (d - today).days <= 7
            except ValueError:
                return False
        filtered = [t for t in filtered if in_week(t.get("due_date"))]
    elif mode.startswith("category:"):
        cat = mode.split(":", 1)[1]
        filtered = [t for t in filtered if t.get("category") == cat]

    # 정렬: (미완료 먼저) -> 마감일 빠른 순 -> 우선순위(상>중>하)
    pr_rank = {"상": 0, "중": 1, "하": 2}
    def sort_key(t: Dict):
        done = 1 if t.get("done") else 0
        due = t.get("due_date") or "9999-12-31"
        pr = pr_rank.get(t.get("priority", "하"), 2)
        return (done, due, pr, t.get("id", 0))

    filtered.sort(key=sort_key)

    print_line()
    print(f"📋 목록 ({mode}) | 총 {len(filtered)}개")
    print_line()
    if not filtered:
        print("표시할 항목이 없습니다.")
        return
    for t in filtered:
        print(format_todo(t))


def progress(todos: List[Dict]):
    if not todos:
        print("아직 Todo가 없습니다. 먼저 추가해 주세요.")
        return
    total = len(todos)
    done = sum(1 for t in todos if t.get("done"))
    pct = round((done / total) * 100, 1)
    print_line()
    print(f"📈 진행률: {done}/{total} 완료 ({pct}%)")
    print_line()


def add_todo(todos: List[Dict]):
    print("\n➕ 새 Todo 추가")
    title = input_text("제목(무엇을 할 건가요?)")
    category = pick_from_list("카테고리 선택", CATEGORIES, default="기타")
    priority = pick_from_list("우선순위 선택", PRIORITIES, default="중")

    while True:
        due_raw = input("마감일(YYYY-MM-DD, Enter=없음): ").strip()
        due = parse_date(due_raw)
        if due_raw.strip() == "" and due is None:
            due = None
            break
        if due is not None:
            break
        print("❗ 날짜 형식이 올바르지 않습니다. 예: 2026-01-15")

    todo = {
        "id": next_id(todos),
        "title": title,
        "category": category,
        "priority": priority,
        "due_date": due,
        "done": False,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "updated_at": None,
        "notes": ""
    }
    todos.append(todo)
    save_todos(todos)
    print("✅ 추가 완료!")
    print(format_todo(todo))


def find_by_id(todos: List[Dict], tid: int) -> Optional[Dict]:
    for t in todos:
        if t.get("id") == tid:
            return t
    return None


def mark_done(todos: List[Dict]):
    s = input_text("완료 처리할 ID를 입력", allow_empty=False)
    if not s.isdigit():
        print("❗ 숫자 ID를 입력해 주세요.")
        return
    tid = int(s)
    t = find_by_id(todos, tid)
    if not t:
        print("❗ 해당 ID가 없습니다.")
        return
    t["done"] = True
    t["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    save_todos(todos)
    print("✅ 완료 처리!")
    print(format_todo(t))


def reopen(todos: List[Dict]):
    s = input_text("미완료로 되돌릴 ID를 입력", allow_empty=False)
    if not s.isdigit():
        print("❗ 숫자 ID를 입력해 주세요.")
        return
    tid = int(s)
    t = find_by_id(todos, tid)
    if not t:
        print("❗ 해당 ID가 없습니다.")
        return
    t["done"] = False
    t["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    save_todos(todos)
    print("✅ 미완료로 변경!")
    print(format_todo(t))


def edit_todo(todos: List[Dict]):
    s = input_text("수정할 ID를 입력", allow_empty=False)
    if not s.isdigit():
        print("❗ 숫자 ID를 입력해 주세요.")
        return
    tid = int(s)
    t = find_by_id(todos, tid)
    if not t:
        print("❗ 해당 ID가 없습니다.")
        return

    print("\n✏️ Todo 수정 (Enter=기존값 유지)")
    t["title"] = input_text("제목", default=t.get("title", ""), allow_empty=False)
    t["category"] = pick_from_list("카테고리", CATEGORIES, default=t.get("category", "기타"))
    t["priority"] = pick_from_list("우선순위", PRIORITIES, default=t.get("priority", "중"))

    while True:
        due_raw = input(f"마감일(YYYY-MM-DD, Enter=기존값 유지 / '-' 입력=없음) [현재:{t.get('due_date') or '-'}]: ").strip()
        if due_raw == "":
            break
        if due_raw == "-":
            t["due_date"] = None
            break
        due = parse_date(due_raw)
        if due is not None:
            t["due_date"] = due
            break
        print("❗ 날짜 형식이 올바르지 않습니다. 예: 2026-01-15")

    notes = input(f"메모(Enter=유지) [현재:{'있음' if t.get('notes') else '없음'}]: ").strip()
    if notes != "":
        t["notes"] = notes

    t["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    save_todos(todos)
    print("✅ 수정 완료!")
    print(format_todo(t))


def delete_todo(todos: List[Dict]):
    s = input_text("삭제할 ID를 입력", allow_empty=False)
    if not s.isdigit():
        print("❗ 숫자 ID를 입력해 주세요.")
        return
    tid = int(s)
    t = find_by_id(todos, tid)
    if not t:
        print("❗ 해당 ID가 없습니다.")
        return

    print(format_todo(t))
    confirm = input("정말 삭제할까요? (y/N): ").strip().lower()
    if confirm != "y":
        print("취소했습니다.")
        return

    todos[:] = [x for x in todos if x.get("id") != tid]
    save_todos(todos)
    print("🗑 삭제 완료!")


def quick_seed(todos: List[Dict]):
    """
    커리어캐쳐 강의 기반: 샘플 Todo 자동 생성
    """
    if todos:
        print("이미 Todo가 있습니다. (샘플은 빈 상태에서만 추천)")
        confirm = input("그래도 샘플을 추가할까요? (y/N): ").strip().lower()
        if confirm != "y":
            return

    samples = [
        ("기업 분석 3개 정리(핵심가치/사업/채용포인트)", "기업분석", "중", None),
        ("자소서 STAR 1개 완성(문제-행동-성과)", "자소서", "상", None),
        ("포트폴리오 프로젝트 1개 정리(성과 중심)", "포폴", "상", None),
        ("면접 질문 10개 답변 구조 작성", "면접", "중", None),
        ("AI로 초안 만들고 내 경험 문장으로 리라이팅", "AI활용", "중", None),
    ]

    for title, cat, pr, due in samples:
        todos.append({
            "id": next_id(todos),
            "title": title,
            "category": cat,
            "priority": pr,
            "due_date": due,
            "done": False,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "updated_at": None,
            "notes": ""
        })

    save_todos(todos)
    print("✅ 샘플 Todo를 추가했습니다.")


def menu():
    print("\n" + "=" * 70)
    print("🎯 Career Todo (커리어캐쳐 버전) - 초심자용 콘솔 앱")
    print("=" * 70)
    print("1) 전체 목록 보기")
    print("2) 미완료만 보기")
    print("3) 완료만 보기")
    print("4) 오늘 마감 보기")
    print("5) 이번 주 마감 보기(7일)")
    print("6) 카테고리별 보기")
    print("7) Todo 추가")
    print("8) Todo 수정")
    print("9) 완료 처리")
    print("10) 미완료로 되돌리기")
    print("11) 삭제")
    print("12) 진행률 보기")
    print("13) 샘플 Todo 넣기(커리어캐쳐 기본 세트)")
    print("0) 종료")


def main():
    todos = load_todos()

    while True:
        try:
            menu()
            choice = input("\n번호 선택: ").strip()

            if choice == "1":
                list_todos(todos, "all")
            elif choice == "2":
                list_todos(todos, "open")
            elif choice == "3":
                list_todos(todos, "done")
            elif choice == "4":
                list_todos(todos, "today")
            elif choice == "5":
                list_todos(todos, "week")
            elif choice == "6":
                cat = pick_from_list("카테고리 선택", CATEGORIES)
                list_todos(todos, f"category:{cat}")
            elif choice == "7":
                add_todo(todos)
                todos = load_todos()
            elif choice == "8":
                edit_todo(todos)
                todos = load_todos()
            elif choice == "9":
                mark_done(todos)
                todos = load_todos()
            elif choice == "10":
                reopen(todos)
                todos = load_todos()
            elif choice == "11":
                delete_todo(todos)
                todos = load_todos()
            elif choice == "12":
                progress(todos)
            elif choice == "13":
                quick_seed(todos)
                todos = load_todos()
            elif choice == "0":
                print("\n👋 종료합니다. (데이터는 {}에 저장되어 있어요)".format(DATA_FILE))
                break
            else:
                print("❗ 올바른 번호를 선택해 주세요.")
        except KeyboardInterrupt:
            print("\n\n👋 사용자 요청으로 종료합니다. 안전하게 저장됩니다.")
            break


if __name__ == "__main__":
    main()
