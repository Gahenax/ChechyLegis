import sqlite3
conn = sqlite3.connect('judicial_archive.db')
conn.execute("UPDATE hotel_rooms SET existing_url = '/static/index.html' WHERE slug = 'chechylegis'")
conn.commit()
conn.close()
print("Updated existing_url for chechylegis")
