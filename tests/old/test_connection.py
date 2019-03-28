import requests
from mapswipe_workers.basic import BaseFunctions


class myRequestsSession(requests.Session):

    def __init__(self):
        super(myRequestsSession, self).__init__()

    def get(self, request_ref, headers, timeout=30):
        print('Using customized get request with a timeout of 30 seconds.')
        return super(myRequestsSession, self).get(request_ref, headers=headers, timeout=timeout)


def test_firebase_connection():

    firebase, postgres = BaseFunctions.get_environment('development')
    fb_db = firebase.database()
    fb_db.requests.get = myRequestsSession().get


    request_object = fb_db.child("groups").child("1002").get().val()


if __name__ == '__main__':
    test_firebase_connection()
    print("Everything passed")