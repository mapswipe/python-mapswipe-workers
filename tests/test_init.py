import json
from mapswipe_workers.basic import BaseFunctions


def upload_sample_data_to_firebase():
    firebase, postgres = BaseFunctions.get_environment('production')
    fb_db = firebase.database()

    with open('sample_data.json') as f:
        sample_data = json.load(f) 

    all_imports_pre = fb_db.child("imports").get()

    for data in sample_data:
        fb_db.child("imports").push(sample_data[data])

    all_imports_post = fb_db.child("imports").get()
    new_imports = []
    for i in all_imports_post.each():
        if all_imports_pre is not None:
            for i2 in all_imports_pre.each():
                if i.key() == i2.key():
                    break
                else:
                    continue
        new_imports.append(i.key())
    print(new_imports)


if __name__ == '__main__':
    upload_sample_data_to_firebase()
    print("Everything passed")
