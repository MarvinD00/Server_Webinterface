import sqlite3

def generate_db():
	conn = sqlite3.connect('users.db')
	c = conn.cursor()
	c.execute('''CREATE TABLE IF NOT EXISTS users (name TEXT PRIMARY KEY,  password TEXT)''')
	conn.commit()
	conn.close()

def add_user(name, password):
	conn = sqlite3.connect('users.db')
	c = conn.cursor()
	if not check_user(name, password):
		c.execute('''INSERT INTO users (name, password) VALUES (?, ?)''', (name, password))
	else :
		print("User already exists")
	conn.commit()
	conn.close()

def check_user(name, password):
	conn = sqlite3.connect('users.db')
	c = conn.cursor()
	c.execute('''SELECT * FROM users WHERE name = ? AND password = ?''', (name, password))
	result = c.fetchone()
	conn.close()
	return result is not None