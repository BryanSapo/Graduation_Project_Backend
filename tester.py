from tinydb import TinyDB,Query

db=TinyDB('temi.json')
# db.truncate()
temi = Query()
last_row = db.get(temi.id=="51288253-3c57-4b91-b9a8-334ab3ebf2e7")
print(last_row)