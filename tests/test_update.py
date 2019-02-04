from mapswipe_workers.basic import BaseFunctions

# make sure that there is a project in firebase and postgres to update
# e.g. import a project first


# make sure that there are results for this project
# make sure that different users contributed to this project


# make sure that results for this project are transfered from firebase to postgresql


# update project contributors and progress for this project
filter = [] # add project ids here
BaseFunctions.run_update(filter)

# check if updated values are as expected

