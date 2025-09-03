import sqlite3
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import csv
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
app.geometry("900x600")

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
tree = ttk.Treeview(app, columns=columns, show="headings", height=15)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=120)
tree.pack(fill="both", expand=True, padx=10, pady=10)

# Label for statistics
stats_label = tb.Label(app, text="", bootstyle="info")
stats_label.pack(pady=5)

# CRUD + Extra functions
def refresh_table(order_by=None, category_filter=None):
    for row in tree.get_children():
        tree.delete(row)
    
    query = "SELECT * FROM documentaries"
    params = ()
    if category_filter:
        query += " WHERE category=?"
        params = (category_filter,)
    if order_by:
        query += f" ORDER BY {order_by}"

    cursor.execute(query, params)
    rows = cursor.fetchall()

    for row in rows:
        tree.insert("", "end", values=row)
    
    update_stats()

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
    update_stats()

def clear_form():
    title_entry.delete(0, tk.END)
    director_entry.delete(0, tk.END)
    year_entry.delete(0, tk.END)
    category_entry.delete(0, tk.END)
    rating_entry.delete(0, tk.END)

def export_csv():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    if file_path:
        cursor.execute("SELECT * FROM documentaries")
        rows = cursor.fetchall()
        with open(file_path, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(rows)
        messagebox.showinfo("Exported", f"Data exported to {file_path}")

def update_stats():
    cursor.execute("SELECT COUNT(*), AVG(rating) FROM documentaries")
    count, avg_rating = cursor.fetchone()
    stats_label.config(text=f"📊 Total: {count} documentaries | ⭐ Avg. Rating: {round(avg_rating,2) if avg_rating else 'N/A'}")

def on_row_double_click(event):
    selected = tree.selection()
    if selected:
        values = tree.item(selected[0])['values']
        clear_form()
        title_entry.insert(0, values[1])
        director_entry.insert(0, values[2])
        year_entry.insert(0, values[3])
        category_entry.insert(0, values[4])
        rating_entry.insert(0, values[5])

# Buttons
btn_frame = tb.Frame(app, padding=10)
btn_frame.pack(fill="x")

tb.Button(btn_frame, text="Add", bootstyle="success", command=add_doc).pack(side="left", padx=5)
tb.Button(btn_frame, text="Update", bootstyle="info", command=update_doc).pack(side="left", padx=5)
tb.Button(btn_frame, text="Delete", bootstyle="danger", command=delete_doc).pack(side="left", padx=5)
tb.Button(btn_frame, text="Search", bootstyle="warning", command=search_doc).pack(side="left", padx=5)
tb.Button(btn_frame, text="Refresh", bootstyle="secondary", command=lambda: refresh_table()).pack(side="left", padx=5)
tb.Button(btn_frame, text="Clear", bootstyle="dark", command=clear_form).pack(side="left", padx=5)
tb.Button(btn_frame, text="Export CSV", bootstyle="primary", command=export_csv).pack(side="left", padx=5)

# Sorting and filtering
sort_frame = tb.Frame(app, padding=10)
sort_frame.pack(fill="x")

tb.Label(sort_frame, text="Sort by:").pack(side="left", padx=5)
tb.Button(sort_frame, text="Year", bootstyle="secondary", command=lambda: refresh_table("year")).pack(side="left", padx=5)
tb.Button(sort_frame, text="Rating", bootstyle="secondary", command=lambda: refresh_table("rating DESC")).pack(side="left", padx=5)

tb.Label(sort_frame, text="Filter by Category:").pack(side="left", padx=10)
filter_entry = tb.Entry(sort_frame, width=20)
filter_entry.pack(side="left", padx=5)
tb.Button(sort_frame, text="Apply Filter", bootstyle="info", command=lambda: refresh_table(None, filter_entry.get())).pack(side="left", padx=5)

# Double-click event for editing
tree.bind("<Double-1>", on_row_double_click)

# Load data initially
refresh_table()

app.mainloop()
conn.close()
