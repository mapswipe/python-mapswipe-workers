git pull
python3 test_config.py
docker-compose build --no-cache postgres
docker-compose build --no-cache firebase_deploy
docker-compose build --no-cache mapswipe_workers
docker-compose build --no-cache manager_dashboard
docker-compose build --no-cache nginx
docker-compose build --no-cache api
docker-compose up -d --force-recreate postgres firebase_deploy mapswipe_workers manager_dashboard nginx api
docker logs firebase_deploy
docker ps -a
