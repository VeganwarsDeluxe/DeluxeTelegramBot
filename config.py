import os

mongo_url = os.environ["mongo_url"]
bot_token = os.environ['bot_token']

boot_chat = int(os.environ['boot_chat'])
admin = int(os.environ.get('admin', '0'))
admin_ids = [int(admin_id) for admin_id in os.environ.get("admin_ids", "0").split(",")]+[admin]
