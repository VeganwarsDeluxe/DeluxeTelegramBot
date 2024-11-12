import os

mongo_url = os.getenv("mongo_url")
bot_token = os.getenv('bot_token')
default_locale = os.getenv('default_locale')

boot_chat = int(os.getenv('boot_chat', 0))
admin = int(os.getenv('admin', '0'))
admin_ids = [int(admin_id) for admin_id in os.getenv("admin_ids", "0").split(",")]+[admin]

db_url = os.getenv('db_url')
