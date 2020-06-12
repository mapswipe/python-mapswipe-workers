from mapswipe_workers.utils import user_management
import random
import string

random_string = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
email = f"test_{random_string}@mapswipe.org"
username = f"test_{random_string}"
password = "mapswipe"
new_username = f"test_new_{random_string}"

try:
    user = user_management.create_user(email, username, password)
    user_management.update_username(email, new_username)
    normal_user = user_management.sign_in_with_email_and_password(email, password)

    path = "/v2/users/test_write"  # make sure that path starts with '/'
    data = {"test_write": "successful"}
    user_management.set_firebase_db(path, data, normal_user["idToken"])

    path = f"/v2/users/{user.uid}/test_write"  # make sure that path starts with '/'
    data = {"test_write": "successful"}
    user_management.set_firebase_db(path, data, normal_user["idToken"])

    path = f"/v2/users/{user.uid}"  # make sure that path starts with '/'
    data = {"test_write": None}
    user_management.update_firebase_db(path, data, normal_user["idToken"])

    path = f"/v2/projectDrafts/test_write"  # make sure that path starts with '/'
    data = {"test_write": "successful"}
    user_management.set_firebase_db(path, data, normal_user["idToken"])

    # user is now project manager
    user_management.set_project_manager_rights(email)
    project_manager = user_management.sign_in_with_email_and_password(email, password)

    path = f"/v2/projectDrafts/test_write"  # make sure that path starts with '/'
    data = {"test_write": "successful"}
    user_management.set_firebase_db(path, data, project_manager["idToken"])

    path = f"/v2/projectDrafts/"  # make sure that path starts with '/'
    data = {"test_write": None}
    user_management.update_firebase_db(path, data, project_manager["idToken"])

    # back to normal
    user_management.remove_project_manager_rights(email)
    user_management.delete_user(email)
except Exception as e:
    user_management.delete_user(email)
    raise Exception
