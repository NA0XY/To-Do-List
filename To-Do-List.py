import json
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from datetime import datetime, timedelta
import time
import csv
from tkcalendar import Calendar
from plyer import notification

# --- Suggest priority and due date based on task name ---
def suggest_priority_and_due(task_name):
    task_name = task_name.lower()
    today = datetime.now().strftime("%Y-%m-%d")
    if "urgent" in task_name or "asap" in task_name:
        return "High", today
    if "tomorrow" in task_name:
        return "Medium", (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    if "meeting" in task_name:
        return "High", today
    if "call" in task_name or "email" in task_name:
        return "Medium", today
    return "Low", (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")

def get_data_dir(app_name="To-Do-List"):
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
    else:
        base = os.path.expanduser("~")
    data_dir = os.path.join(base, app_name)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir

# --- Profile selection dialog ---
def profile_selection_window(root):
    dialog = tk.Toplevel(root)
    dialog.title("Choose Profile")
    dialog.geometry("420x220+{}+{}".format(
        root.winfo_screenwidth()//2 - 210,
        root.winfo_screenheight()//2 - 110
    ))
    dialog.configure(bg="#232946")
    dialog.grab_set()
    dialog.transient(root)

    ttk.Label(dialog, text="Select or Create Profile", font=("Segoe UI", 16, "bold"),
              background="#232946", foreground="#eebbc3").pack(pady=16)
    # Find profiles in the data directory, not current dir!
    data_dir = get_data_dir()
    profiles = [f.replace("tasks_", "").replace(".json", "") for f in os.listdir(data_dir) if f.startswith("tasks_") and f.endswith(".json")]
    profile_var = tk.StringVar()
    profile_combo = ttk.Combobox(dialog, textvariable=profile_var, values=profiles, font=("Segoe UI", 12))
    profile_combo.pack(pady=8)
    profile_combo.configure(width=24)
    ttk.Label(dialog, text="Or enter a new profile name:", background="#232946", foreground="#eebbc3").pack(pady=(10, 2))
    entry = ttk.Entry(dialog, textvariable=profile_var, font=("Segoe UI", 12), width=26)
    entry.pack(pady=2)

    def submit():
        if not profile_var.get().strip():
            messagebox.showwarning("Profile", "Please enter or select a profile name.", parent=dialog)
            return
        dialog.destroy()

    ttk.Button(dialog, text="OK", command=submit).pack(pady=16)
    entry.focus()
    root.wait_window(dialog)
    return profile_var.get().strip() or "default"

# --- Main To-Do App ---
class ModernTodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern To-Do List")
        self.root.geometry("1200x750")
        self.root.configure(bg="#232946")
        self.data_dir = get_data_dir()
        self.profile = profile_selection_window(self.root)
        self.filename = os.path.join(self.data_dir, f"tasks_{self.profile}.json")
        self.tasks = self.load_tasks()

        # --- Style setup ---
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=8, background="#3a86ff", foreground="#fff", borderwidth=0)
        style.map("TButton", background=[("active", "#ffbe0b")])
        style.configure("TLabel", background="#232946", foreground="#eebbc3", font=("Segoe UI", 13))
        style.configure("TEntry", fieldbackground="#b8c1ec", font=("Consolas", 12))

        # --- Header ---
        header = ttk.Label(self.root, text=f"📝 To-Do List ({self.profile})", font=("Segoe UI", 30, "bold"), foreground="#ffbe0b")
        header.pack(pady=18)

        # --- Search and Profile Switch ---
        search_frame = ttk.Frame(self.root)
        search_frame.pack(pady=5)
        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var, width=50, font=("Consolas", 12)).pack(side="left", padx=6)
        ttk.Button(search_frame, text="🔎 Search", command=self.search_task).pack(side="left", padx=6)
        ttk.Button(search_frame, text="👤 Switch Profile", command=self.switch_profile).pack(side="left", padx=6)

        # --- Main content (Task list and Calendar) ---
        content_frame = ttk.Frame(self.root)
        content_frame.pack(fill="both", expand=True, padx=16, pady=6)

        # --- Left: Task list ---
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side="left", fill="both", expand=True)
        self.task_listbox = tk.Listbox(left_frame, width=80, height=25, font=("Consolas", 12), bg="#121629", fg="#e0f7fa",
            selectbackground="#ffbe0b", selectforeground="#232946", activestyle='none', bd=0, highlightthickness=0)
        self.task_listbox.pack(pady=10, padx=10, fill="both", expand=True)

        # --- Right: Calendar ---
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side="right", fill="y", padx=16)
        ttk.Label(right_frame, text="📅 Calendar", font=("Segoe UI", 16, "bold"), foreground="#3a86ff").pack(pady=4)
        self.cal = Calendar(right_frame, selectmode='day', background="#232946", disabledbackground="#b8c1ec", bordercolor="#3a86ff",
                            headersbackground="#3a86ff", normalbackground="#232946", foreground="#eebbc3", weekendbackground="#232946",
                            selectbackground="#ffbe0b", font=("Segoe UI", 11), date_pattern="yyyy-mm-dd")
        self.cal.pack(pady=4)
        ttk.Button(right_frame, text="Show Tasks for Date", command=self.show_tasks_on_calendar_date).pack(pady=4)
        self.cal_tasks_box = tk.Listbox(right_frame, width=30, height=10, font=("Consolas", 11), bg="#232946", fg="#eebbc3",
                                        selectbackground="#ffbe0b", selectforeground="#232946", activestyle='none', bd=0, highlightthickness=0)
        self.cal_tasks_box.pack(pady=4)

        # --- Button bar ---
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=12)
        ttk.Button(button_frame, text="➕ Add Task", command=self.add_task).grid(row=0, column=0, padx=8)
        ttk.Button(button_frame, text="🛠 Update", command=self.update_task).grid(row=0, column=1, padx=8)
        ttk.Button(button_frame, text="❌ Delete", command=self.delete_task).grid(row=0, column=2, padx=8)
        ttk.Button(button_frame, text="✔ Toggle", command=self.toggle_complete).grid(row=0, column=3, padx=8)
        ttk.Button(button_frame, text="✅ Completed", command=self.filter_completed).grid(row=0, column=4, padx=8)
        ttk.Button(button_frame, text="📋 All Tasks", command=self.update_task_listbox).grid(row=0, column=5, padx=8)
        ttk.Button(button_frame, text="📤 Export CSV", command=self.export_to_csv).grid(row=0, column=6, padx=8)

        self.update_task_listbox()
        self.root.after(1200, self.show_daily_summary)

    # --- Profile selection and switching ---
    def select_profile(self):
        return profile_selection_window(self.root)

    def switch_profile(self):
        self.profile = self.select_profile()
        self.filename = os.path.join(self.data_dir, f"tasks_{self.profile}.json")
        self.tasks = self.load_tasks()
        self.update_task_listbox()
        self.root.title(f"To-Do List ({self.profile})")

    # --- Daily summary notification ---
    def show_daily_summary(self):
        today = datetime.now().strftime("%Y-%m-%d")
        due_today = [t for t in self.tasks if t['due'] == today and not t['completed']]
        overdue = [t for t in self.tasks if t['due'] < today and not t['completed']]
        urgent = [t for t in self.tasks if t.get('urgent')]
        summary = f"Due Today: {len(due_today)}\nOverdue: {len(overdue)}\nUrgent: {len(urgent)}"
        messagebox.showinfo("Daily Summary", summary)
        try:
            notification.notify(
                title="To-Do Daily Summary",
                message=summary,
                timeout=10
            )
        except Exception:
            pass

    # --- Data loading and saving ---
    def load_tasks(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as file:
                return json.load(file)
        return []

    def save_tasks(self):
        with open(self.filename, "w") as file:
            json.dump(self.tasks, file, indent=4)

    # --- Popup for adding/updating tasks ---
    def popup_window(self, title, prompts, defaults=None, include_urgent=False, include_subtasks=False, include_notes=False):
        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.geometry("480x540")
        popup.configure(bg="#232946")
        popup.transient(self.root)
        popup.grab_set()
        inputs = {}
        for prompt in prompts:
            ttk.Label(popup, text=prompt).pack(pady=5)
            var = tk.StringVar()
            if defaults and prompt in defaults:
                var.set(defaults[prompt])
            entry = ttk.Entry(popup, textvariable=var, width=40, font=("Consolas", 12))
            entry.pack(pady=5)
            inputs[prompt] = var

        urgent_var = tk.BooleanVar()
        if include_urgent:
            ttk.Checkbutton(popup, text="Mark as Urgent", variable=urgent_var).pack(pady=5)
        subtasks_var = tk.StringVar()
        if include_subtasks:
            ttk.Label(popup, text="Subtasks (comma separated):").pack(pady=5)
            ttk.Entry(popup, textvariable=subtasks_var, width=40).pack(pady=5)
        notes_widget = None
        if include_notes:
            ttk.Label(popup, text="Notes:").pack(pady=5)
            notes_widget = tk.Text(popup, width=40, height=4, font=("Consolas", 11), wrap="word", bg="#b8c1ec")
            notes_widget.pack(pady=5)
            if defaults and "Notes" in defaults:
                notes_widget.insert("1.0", defaults["Notes"])

        result = {}
        def submit():
            for key, var in inputs.items():
                result[key] = var.get()
            if include_urgent:
                result["Urgent"] = urgent_var.get()
            if include_subtasks:
                result["Subtasks"] = [s.strip() for s in subtasks_var.get().split(",") if s.strip()]
            if include_notes and notes_widget:
                result["Notes"] = notes_widget.get("1.0", "end-1c")
            popup.destroy()

        ttk.Button(popup, text="🌈 Submit", command=submit).pack(pady=15)
        self.root.wait_window(popup)
        return result

    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    # --- Add, update, delete, toggle complete ---
    def add_task(self):
        task_name = simpledialog.askstring("Task Name", "Enter task name:")
        if not task_name:
            return
        suggested_priority, suggested_due = suggest_priority_and_due(task_name)
        result = self.popup_window("Add Task", [
            "Task", "Due Date (YYYY-MM-DD)", "Priority (Low/Medium/High)"
        ], defaults={"Task": task_name, "Due Date (YYYY-MM-DD)": suggested_due, "Priority (Low/Medium/High)": suggested_priority},
        include_urgent=True, include_subtasks=True, include_notes=True)
        if result.get("Task") and self.validate_date(result.get("Due Date (YYYY-MM-DD)", "")):
            self.tasks.append({
                "task": result["Task"],
                "due": result["Due Date (YYYY-MM-DD)"],
                "priority": result["Priority (Low/Medium/High)"],
                "completed": False,
                "urgent": result.get("Urgent", False),
                "subtasks": result.get("Subtasks", []),
                "notes": result.get("Notes", "")
            })
            self.save_tasks()
            self.animate_update()
        else:
            messagebox.showerror("Invalid Input", "Please enter a valid date in YYYY-MM-DD format.")

    def update_task(self):
        selected = self.task_listbox.curselection()
        if selected:
            index = selected[0]
            task = self.tasks[index]
            result = self.popup_window("Update Task", [
                "Task", "Due Date (YYYY-MM-DD)", "Priority (Low/Medium/High)"
            ], defaults={
                "Task": task["task"],
                "Due Date (YYYY-MM-DD)": task["due"],
                "Priority (Low/Medium/High)": task["priority"],
                "Notes": task.get("notes", "")
            }, include_urgent=True, include_subtasks=True, include_notes=True)
            if result.get("Task") and self.validate_date(result.get("Due Date (YYYY-MM-DD)", "")):
                self.tasks[index]["task"] = result["Task"]
                self.tasks[index]["due"] = result["Due Date (YYYY-MM-DD)"]
                self.tasks[index]["priority"] = result["Priority (Low/Medium/High)"]
                self.tasks[index]["urgent"] = result.get("Urgent", False)
                self.tasks[index]["subtasks"] = result.get("Subtasks", [])
                self.tasks[index]["notes"] = result.get("Notes", "")
                self.save_tasks()
                self.animate_update()
            else:
                messagebox.showerror("Invalid Input", "Please enter a valid date in YYYY-MM-DD format.")
        else:
            messagebox.showwarning("No Selection", "Please select a task to update.")

    def delete_task(self):
        selected = self.task_listbox.curselection()
        if selected:
            del self.tasks[selected[0]]
            self.save_tasks()
            self.animate_update()
        else:
            messagebox.showwarning("No Selection", "Please select a task to delete.")

    def toggle_complete(self):
        selected = self.task_listbox.curselection()
        if selected:
            index = selected[0]
            self.tasks[index]["completed"] = not self.tasks[index]["completed"]
            self.save_tasks()
            self.animate_update()
        else:
            messagebox.showwarning("No Selection", "Please select a task to toggle completion.")

    # --- Search, filter, and update display ---
    def search_task(self):
        query = self.search_var.get().lower()
        if query:
            filtered = [task for task in self.tasks if query in task["task"].lower()]
            self.update_task_listbox(filtered)

    def filter_completed(self):
        filtered = [task for task in self.tasks if task["completed"]]
        self.update_task_listbox(filtered)

    def update_task_listbox(self, tasks=None):
        if tasks is None:
            tasks = self.tasks
        self.task_listbox.delete(0, tk.END)
        for task in tasks:
            status = "🟢" if task["completed"] else "🔴"
            urgent = "🔥" if task.get("urgent") else ""
            subtasks = f" | Subtasks: {', '.join(task.get('subtasks', []))}" if task.get("subtasks") else ""
            notes = f" | Notes: {task.get('notes', '')}" if task.get("notes") else ""
            display = f"{task['task']} | Due: {task['due']} | Priority: {task['priority']} {urgent} [{status}]{subtasks}{notes}"
            self.task_listbox.insert(tk.END, display)

    # --- Export tasks to CSV file ---
    def export_to_csv(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save Task List As")
        if filepath:
            try:
                with open(filepath, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Task", "Due Date", "Priority", "Urgent", "Completed", "Subtasks", "Notes"])
                    for task in self.tasks:
                        writer.writerow([
                            task['task'], task['due'], task['priority'],
                            "Yes" if task.get('urgent') else "No",
                            "Yes" if task['completed'] else "No",
                            "; ".join(task.get('subtasks', [])),
                            task.get('notes', "")
                        ])
                messagebox.showinfo("Success", f"Tasks exported successfully to {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export tasks: {e}")

    # --- Animation for updates ---
    def animate_update(self):
        for i in range(6):
            self.root.update()
            self.task_listbox.config(bg="#3a86ff" if i % 2 == 0 else "#121629")
            time.sleep(0.04)
        self.update_task_listbox()

    # --- Show tasks for selected calendar date ---
    def show_tasks_on_calendar_date(self):
        date = self.cal.get_date()
        filtered = [t for t in self.tasks if t['due'] == date]
        self.cal_tasks_box.delete(0, tk.END)
        for t in filtered:
            urgent = "🔥" if t.get("urgent") else ""
            self.cal_tasks_box.insert(tk.END, f"{t['task']} {urgent}")

# --- Run the app ---
def main():
    root = tk.Tk()
    ModernTodoApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
