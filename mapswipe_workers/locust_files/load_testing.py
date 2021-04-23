import datetime
import random
from uuid import uuid4

from locust import User, between

from mapswipe_workers.utils import user_management


class MapSwipeUser(User):
    wait_time = between(0.5, 10)

    def __init__(self):
        self.project_id = "-MYg8CEf2k1-RitN62X0"
        random_string = uuid4()
        self.email = f"test_{random_string}@mapswipe.org"
        self.username = f"test_{random_string}"
        self.password = "mapswipe"
        self.user_id = None
        self.signed_in_user = None

    def set_up_user(self):
        # check if is already signed in
        if self.signed_in_user is None:
            print("user is not signed in. Will create a new user.")
            # create user if not exists
            user = user_management.create_user(self.email, self.username, self.password)
            self.user_id = user.uid

            # sign in user
            self.signed_in_user = user_management.sign_in_with_email_and_password(
                self.email, self.password
            )
            print("Created a new user.")
        else:
            print("user is already signed in.")
            pass

    def create_mock_result(self, group):
        start_time = datetime.datetime.utcnow().isoformat()[0:-3] + "Z"
        end_time = datetime.datetime.utcnow().isoformat()[0:-3] + "Z"

        x_min = int(group["xMin"])
        x_max = int(group["xMax"])
        y_min = int(group["yMin"])
        y_max = int(group["yMax"])

        results = {}
        for x in range(x_min, x_max):
            for y in range(y_min, y_max):
                task_id = f"18-{x}-{y}"
                result = random.choices([0, 1, 2, 3])[0]  # no, yes, maybe, bad_imagery
                results[task_id] = result

        data = {
            "results": results,
            "timestamp": end_time,
            "startTime": start_time,
            "endTime": end_time,
        }
        return data

    def map_a_group(self):
        """Get a group from Firebase for this user.

        Make sure that this user has not worked on this group before.
        """

        # get the groups that need to be mapped
        path = f"/v2/groups/{self.project_id}"
        # make sure to set '&' at the end of the string
        custom_arguments = 'orderBy="requiredCount"&limitToLast=15&'
        new_groups = user_management.get_firebase_db(
            path, custom_arguments, self.signed_in_user["idToken"]
        )

        # get the groups the user has worked on already
        path = f"/v2/users/{self.user_id}/contributions/{self.project_id}"
        # make sure to set & at the end of the string
        custom_arguments = "shallow=True&"
        existing_groups = user_management.get_firebase_db(
            path, custom_arguments, self.signed_in_user["idToken"]
        )

        # pick group for mapping
        # Get difference between new_groups and existing groups.
        # We should get the groups the user has not yet worked on.
        if existing_groups is None:
            next_group_id = random.choice(list(new_groups.keys()))
        else:
            existing_groups.pop(
                "taskContributionCount", None
            )  # need to remove this since it is no groupId
            remaining_group_ids = list(
                set(new_groups.keys()) - set(existing_groups.keys())
            )
            next_group_id = random.choice(remaining_group_ids)

        # get group object
        next_group = new_groups[next_group_id]

        # create mock result for this group
        result = self.create_mock_result(next_group)

        # upload results in firebase
        path = f"/v2/results/{self.project_id}/{next_group_id}/{self.user_id}"
        user_management.set_firebase_db(path, result, self.signed_in_user["idToken"])


if __name__ == "__main__":
    mapswipe_user = MapSwipeUser()
    mapswipe_user.set_up_user()
    mapswipe_user.map_a_group()
    mapswipe_user.map_a_group()
    mapswipe_user.map_a_group()
