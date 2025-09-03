import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import ttkbootstrap as tb

# Database setup
conn = sqlite3.connect("documentaries.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS documentaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    director TEXT,
    year INTEGER,
    category TEXT,
    rating REAL
)
""")
conn.commit()

# App window
app = tb.Window(themename="cyborg")
app.title("🎬 Documentary Management System")
app.geometry("800x500")

# Frame for form
form_frame = tb.Frame(app, padding=10)
form_frame.pack(fill="x")

# Input fields
tb.Label(form_frame, text="Title:").grid(row=0, column=0, padx=5, pady=5)
title_entry = tb.Entry(form_frame, width=30)
title_entry.grid(row=0, column=1, padx=5, pady=5)

tb.Label(form_frame, text="Director:").grid(row=1, column=0, padx=5, pady=5)
director_entry = tb.Entry(form_frame, width=30)
director_entry.grid(row=1, column=1, padx=5, pady=5)

tb.Label(form_frame, text="Year:").grid(row=0, column=2, padx=5, pady=5)
year_entry = tb.Entry(form_frame, width=10)
year_entry.grid(row=0, column=3, padx=5, pady=5)

tb.Label(form_frame, text="Category:").grid(row=1, column=2, padx=5, pady=5)
category_entry = tb.Entry(form_frame, width=20)
category_entry.grid(row=1, column=3, padx=5, pady=5)

tb.Label(form_frame, text="Rating (1-10):").grid(row=0, column=4, padx=5, pady=5)
rating_entry = tb.Entry(form_frame, width=10)
rating_entry.grid(row=0, column=5, padx=5, pady=5)

# Table for data display
columns = ("ID", "Title", "Director", "Year", "Category", "Rating")
tree = ttk.Treeview(app, columns=columns, show="headings", height=12)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100)
tree.pack(fill="both", expand=True, padx=10, pady=10)

# CRUD functions
def refresh_table():
    for row in tree.get_children():
        tree.delete(row)
    cursor.execute("SELECT * FROM documentaries")
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)

def add_doc():
    title, director, year, category, rating = (
        title_entry.get(),
        director_entry.get(),
        year_entry.get(),
        category_entry.get(),
        rating_entry.get()
    )
    if not (title and director and year and category and rating):
        messagebox.showerror("Error", "All fields are required")
        return
    try:
        cursor.execute("INSERT INTO documentaries (title, director, year, category, rating) VALUES (?, ?, ?, ?, ?)",
                       (title, director, int(year), category, float(rating)))
        conn.commit()
        refresh_table()
        clear_form()
        messagebox.showinfo("Success", f"'{title}' added successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def delete_doc():
    selected = tree.selection()
    if not selected:
        messagebox.showerror("Error", "Select a documentary to delete")
        return
    doc_id = tree.item(selected[0])['values'][0]
    cursor.execute("DELETE FROM documentaries WHERE id=?", (doc_id,))
    conn.commit()
    refresh_table()
    messagebox.showinfo("Deleted", "Documentary deleted")

def update_doc():
    selected = tree.selection()
    if not selected:
        messagebox.showerror("Error", "Select a documentary to update")
        return
    doc_id = tree.item(selected[0])['values'][0]
    title, director, year, category, rating = (
        title_entry.get(),
        director_entry.get(),
        year_entry.get(),
        category_entry.get(),
        rating_entry.get()
    )
    if not (title and director and year and category and rating):
        messagebox.showerror("Error", "All fields are required")
        return
    cursor.execute("UPDATE documentaries SET title=?, director=?, year=?, category=?, rating=? WHERE id=?",
                   (title, director, int(year), category, float(rating), doc_id))
    conn.commit()
    refresh_table()
    clear_form()
    messagebox.showinfo("Updated", "Documentary updated successfully!")

def search_doc():
    query = title_entry.get()
    for row in tree.get_children():
        tree.delete(row)
    cursor.execute("SELECT * FROM documentaries WHERE title LIKE ?", ('%' + query + '%',))
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)

def clear_form():
    title_entry.delete(0, tk.END)
    director_entry.delete(0, tk.END)
    year_entry.delete(0, tk.END)
    category_entry.delete(0, tk.END)
    rating_entry.delete(0, tk.END)

# Buttons
btn_frame = tb.Frame(app, padding=10)
btn_frame.pack(fill="x")

tb.Button(btn_frame, text="Add", bootstyle="success", command=add_doc).pack(side="left", padx=5)
tb.Button(btn_frame, text="Update", bootstyle="info", command=update_doc).pack(side="left", padx=5)
tb.Button(btn_frame, text="Delete", bootstyle="danger", command=delete_doc).pack(side="left", padx=5)
tb.Button(btn_frame, text="Search", bootstyle="warning", command=search_doc).pack(side="left", padx=5)
tb.Button(btn_frame, text="Refresh", bootstyle="secondary", command=refresh_table).pack(side="left", padx=5)
tb.Button(btn_frame, text="Clear", bootstyle="dark", command=clear_form).pack(side="left", padx=5)

# Load data initially
refresh_table()

app.mainloop()
conn.close()
