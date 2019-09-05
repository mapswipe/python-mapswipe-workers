from mapswipe_workers.utils import user_management
import random
import string

random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
email = f'test_{random_string}@mapswipe.org'
username = f'test_{random_string}'
password = 'mapswipe'
new_username = f'test_new_{random_string}'

user_management.create_user(email, username, password)
user_management.update_username(email, new_username)
user_management.set_project_manager_rights(email)
user_management.remove_project_manager_rights(email)
user_management.delete_user(email)


