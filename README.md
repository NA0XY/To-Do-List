# To-Do List
A beginner-friendly, modern, and feature-rich To-Do List application built with Python and Tkinter.
This app lets you manage your daily tasks with priorities, due dates, subtasks, notes, calendar view, notifications, and more—all in a beautiful, easy-to-use interface.

✨ Features
Multiple Profiles: Each user/profile has their own separate task list.

Add, Update, Delete Tasks: Easily manage your to-dos.

Mark as Completed: Toggle tasks as done/undone.

Priorities & Due Dates: Assign priority and deadline to each task.

Urgent Flag: Mark tasks as urgent for extra visibility.

Subtasks & Notes: Add subtasks and notes to any task.

AI Suggestions: Automatically suggests a priority and due date based on your task name.

Search & Filter: Search tasks or show only completed ones.

Calendar View: See tasks by date in a calendar widget.

Daily Summary: Get a daily popup and system notification of tasks due, overdue, and urgent.

Export to CSV: Save your tasks as a CSV file for backup or sharing.

Modern UI: Clean, colorful, and responsive interface.

🖥️ Screenshots
![Screenshot
(Add your screenshot here)

🚀 Getting Started
1. Install Python
Python 3.8 or newer is recommended.

2. Install Required Packages
Open your terminal or command prompt and run:

bash
pip install tkcalendar plyer

3. Download the Code
Save the code as todo.py (or your preferred filename).

4. Run the App
bash
python todo.py
📝 Usage
Choose or Create a Profile:
On first launch, enter a profile name (e.g., your name) to keep tasks separate for each user.

Add a Task:
Click "➕ Add Task" and fill in the details. The app will suggest a priority and due date based on the task name.

Update or Delete:
Select a task in the list and click "🛠 Update" or "❌ Delete".

Mark as Completed:
Select a task and click "✔ Toggle" to mark it as done or undone.

Filter and Search:
Use the search bar to find tasks, or click "✅ Completed" to show only finished tasks.

Calendar View:
Use the calendar on the right to see tasks due on a specific date.

Export Tasks:
Click "📤 Export CSV" to save your tasks as a CSV file.

Daily Summary:
On launch, you'll see a summary popup and a desktop notification of your most important tasks for today.

💡 Customization
Window Size:
The default is 1200x750 for best appearance. Adjust self.root.geometry("1200x750") if needed.

Colors and Fonts:
You can tweak the color codes and font names in the code for your own style.

🛠️ Code Structure
todo.py: The main application file.

tasks_{profile}.json: Each profile's tasks are saved in a separate file.

🧑‍💻 Requirements
Python 3.8+

tkcalendar

plyer

🙋 FAQ
Q: I get an error about tkcalendar or plyer not found!
A: Make sure you have installed them with pip install tkcalendar plyer.

Q: Where are my tasks saved?
A: In a file called tasks_{yourprofilename}.json in the same folder as the script.

Q: Can I use this on Mac or Linux?
A: Yes! Tkinter, tkcalendar, and plyer work cross-platform.

📚 Credits
Built with Tkinter, tkcalendar, and plyer.

Inspired by GeeksForGeeks To-Do List and DataFlair.

📄 License
This project is free to use and modify for personal or educational purposes.

Happy tasking!
