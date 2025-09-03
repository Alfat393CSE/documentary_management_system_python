import sqlite3
from tabulate import tabulate

# Connect to SQLite
conn = sqlite3.connect("documentaries.db")
cursor = conn.cursor()

# Create table
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

# Add documentary
def add_documentary(title, director, year, category, rating):
    cursor.execute("INSERT INTO documentaries (title, director, year, category, rating) VALUES (?, ?, ?, ?, ?)",
                   (title, director, year, category, rating))
    conn.commit()
    print(f"✅ Documentary '{title}' added successfully!")

# View all
def view_all():
    cursor.execute("SELECT * FROM documentaries")
    rows = cursor.fetchall()
    if rows:
        print(tabulate(rows, headers=["ID", "Title", "Director", "Year", "Category", "Rating"], tablefmt="grid"))
    else:
        print("📂 No documentaries found.")

# Search
def search(title):
    cursor.execute("SELECT * FROM documentaries WHERE title LIKE ?", ('%' + title + '%',))
    rows = cursor.fetchall()
    if rows:
        print(tabulate(rows, headers=["ID", "Title", "Director", "Year", "Category", "Rating"], tablefmt="grid"))
    else:
        print("❌ No results found.")

# Delete
def delete(doc_id):
    cursor.execute("DELETE FROM documentaries WHERE id = ?", (doc_id,))
    conn.commit()
    print("🗑️ Documentary deleted.")

# Menu
def menu():
    while True:
        print("\n🎬 Documentary Management System")
        print("1. Add Documentary")
        print("2. View All")
        print("3. Search by Title")
        print("4. Delete Documentary")
        print("5. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            title = input("Enter Title: ")
            director = input("Enter Director: ")
            year = int(input("Enter Year: "))
            category = input("Enter Category: ")
            rating = float(input("Enter Rating (1-10): "))
            add_documentary(title, director, year, category, rating)
        elif choice == "2":
            view_all()
        elif choice == "3":
            title = input("Enter Title to Search: ")
            search(title)
        elif choice == "4":
            doc_id = int(input("Enter Documentary ID to Delete: "))
            delete(doc_id)
        elif choice == "5":
            print("👋 Exiting... Goodbye!")
            break
        else:
            print("❌ Invalid choice!")

# Run program
menu()
conn.close()
