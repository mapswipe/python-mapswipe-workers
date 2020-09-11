git pull
if [[$?=0]]
then
echo "success"
else
echo "failure: $?"
exit
fi

python3 test_config.py
if [[$?=0]]
then
echo "success"
else
echo "failure: $?"
exit
fi

docker-compose build - -no-cache postgres
if [[$?=0]]
then
echo "success"
else
echo "failure: $?"
exit
fi

docker-compose build - -no-cache firebase_deploy
if [[$?=0]]
then
echo "success"
else
echo "failure: $?"
exit
fi

docker-compose build - -no-cache mapswipe_workers
if [[$?=0]]
then
echo "success"
else
echo "failure: $?"
exit
fi

docker-compose build - -no-cache manager_dashboard
if [[$?=0]]
then
echo "success"
else
echo "failure: $?"
exit
fi

docker-compose build - -no-cache nginx
if [[$?=0]]
then
echo "success"
else
echo "failure: $?"
exit
fi

docker-compose build - -no-cache api
if [[$?=0]]
then
echo "success"
else
echo "failure: $?"
exit
fi

docker-compose up - d - -force-recreate postgres firebase_deploy mapswipe_workers manager_dashboard nginx api
if [[$?=0]]
then
echo "success"
else
echo "failure: $?"
exit
fi

docker logs firebase_deploy
if [[$?=0]]
then
echo "success"
else
echo "failure: $?"
exit
fi

docker ps - a
if [[$?=0]]
then
echo "success"
else
echo "failure: $?"
exit
fi
