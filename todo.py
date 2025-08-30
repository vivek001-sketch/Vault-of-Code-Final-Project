#!/usr/bin/env python3
"""
Personal To-Do List Application (CLI)
- Add, view, edit, complete, delete tasks
- Categories (e.g., Work, Personal, Urgent)
- JSON persistence across runs

Run:
    python todo.py
"""

import json
import os
from dataclasses import dataclass, asdict, field
from typing import List, Optional

DATA_FILE = "tasks.json"
CATEGORIES = ["Work", "Personal", "Urgent", "Other"]

@dataclass
class Task:
    title: str
    description: str
    category: str
    completed: bool = False

    def mark_completed(self):
        self.completed = True

def save_tasks(tasks: List[Task], path: str = DATA_FILE) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump([asdict(t) for t in tasks], f, indent=2, ensure_ascii=False)

def load_tasks(path: str = DATA_FILE) -> List[Task]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Backward safety: if any dict missing keys, handle gracefully
    tasks: List[Task] = []
    for d in data:
        tasks.append(Task(
            title=d.get("title", ""),
            description=d.get("description", ""),
            category=d.get("category", "Other"),
            completed=bool(d.get("completed", False)),
        ))
    return tasks

def clear_screen():
    try:
        os.system("cls" if os.name == "nt" else "clear")
    except Exception:
        pass

def pause():
    input("\nPress Enter to continue...")

def print_header(title: str):
    print("=" * 60)
    print(title.center(60))
    print("=" * 60)

def choose_category() -> str:
    print("Select a category:")
    for idx, cat in enumerate(CATEGORIES, start=1):
        print(f"{idx}. {cat}")
    choice = input("Enter choice (1-{}), or type a new category: ".format(len(CATEGORIES))).strip()
    if choice.isdigit():
        idx = int(choice)
        if 1 <= idx <= len(CATEGORIES):
            return CATEGORIES[idx - 1]
    # otherwise treat as free-text category
    return choice if choice else "Other"

def add_task(tasks: List[Task]):
    clear_screen()
    print_header("Add Task")
    title = input("Title: ").strip()
    description = input("Description: ").strip()
    category = choose_category()
    if not title:
        print("Title cannot be empty. Task not added.")
    else:
        tasks.append(Task(title=title, description=description, category=category))
        print("✅ Task added!")

def list_tasks(tasks: List[Task], *, show_index: bool = True, filter_category: Optional[str] = None, filter_status: Optional[str] = None):
    if not tasks:
        print("No tasks found.")
        return

    filtered = tasks
    if filter_category:
        filtered = [t for t in filtered if t.category.lower() == filter_category.lower()]
    if filter_status == "completed":
        filtered = [t for t in filtered if t.completed]
    elif filter_status == "pending":
        filtered = [t for t in filtered if not t.completed]

    if not filtered:
        print("No tasks match the filter.")
        return

    print("{:<5} {:<25} {:<12} {:<10} {}".format("#", "Title", "Category", "Status", "Description"))
    print("-" * 60)
    for i, t in enumerate(filtered, start=1):
        status = "Done" if t.completed else "Pending"
        idx_label = f"{i}." if show_index else ""
        print("{:<5} {:<25} {:<12} {:<10} {}".format(idx_label, t.title[:25], t.category[:12], status, t.description))

def _select_task_index(tasks: List[Task]) -> Optional[int]:
    if not tasks:
        print("No tasks to select.")
        return None
    list_tasks(tasks)
    choice = input("\nEnter task number to select: ").strip()
    if not choice.isdigit():
        print("Invalid input.")
        return None
    idx = int(choice) - 1
    if 0 <= idx < len(tasks):
        return idx
    print("Invalid task number.")
    return None

def mark_task_completed(tasks: List[Task]):
    clear_screen()
    print_header("Mark Task as Completed")
    idx = _select_task_index(tasks)
    if idx is None:
        return
    tasks[idx].mark_completed()
    print("✅ Task marked as completed.")

def delete_task(tasks: List[Task]):
    clear_screen()
    print_header("Delete Task")
    idx = _select_task_index(tasks)
    if idx is None:
        return
    deleted = tasks.pop(idx)
    print(f"🗑️  Deleted: {deleted.title}")

def edit_task(tasks: List[Task]):
    clear_screen()
    print_header("Edit Task")
    idx = _select_task_index(tasks)
    if idx is None:
        return
    t = tasks[idx]
    print(f"Editing: {t.title}")
    new_title = input(f"New title (leave blank to keep '{t.title}'): ").strip()
    new_desc = input(f"New description (leave blank to keep current): ").strip()
    print(f"Current category: {t.category}")
    change_cat = input("Change category? (y/N): ").strip().lower() == 'y'
    if change_cat:
        new_cat = choose_category()
    else:
        new_cat = t.category

    if new_title:
        t.title = new_title
    if new_desc:
        t.description = new_desc
    t.category = new_cat
    print("✏️  Task updated.")

def view_tasks_menu(tasks: List[Task]):
    while True:
        clear_screen()
        print_header("View Tasks")
        print("1. View All")
        print("2. View by Category")
        print("3. View Pending Only")
        print("4. View Completed Only")
        print("5. Back")
        choice = input("Choose an option: ").strip()
        clear_screen()
        print_header("Tasks")
        if choice == "1":
            list_tasks(tasks)
            pause()
        elif choice == "2":
            cat = input("Enter category to filter by: ").strip()
            list_tasks(tasks, filter_category=cat)
            pause()
        elif choice == "3":
            list_tasks(tasks, filter_status="pending")
            pause()
        elif choice == "4":
            list_tasks(tasks, filter_status="completed")
            pause()
        elif choice == "5":
            return
        else:
            print("Invalid choice.")
            pause()

def main():
    tasks = load_tasks(DATA_FILE)
    while True:
        clear_screen()
        print_header("Personal To-Do List")
        print("1. Add Task")
        print("2. View Tasks")
        print("3. Edit Task")
        print("4. Mark Task Completed")
        print("5. Delete Task")
        print("6. Exit")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            add_task(tasks)
            save_tasks(tasks, DATA_FILE)
            pause()
        elif choice == "2":
            view_tasks_menu(tasks)
        elif choice == "3":
            edit_task(tasks)
            save_tasks(tasks, DATA_FILE)
            pause()
        elif choice == "4":
            mark_task_completed(tasks)
            save_tasks(tasks, DATA_FILE)
            pause()
        elif choice == "5":
            delete_task(tasks)
            save_tasks(tasks, DATA_FILE)
            pause()
        elif choice == "6":
            save_tasks(tasks, DATA_FILE)
            print("Goodbye! 👋")
            break
        else:
            print("Invalid option.")
            pause()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
