python3 test_config.py
sudo docker-compose build --no-cache
sudo docker-compose up -d --force-recreate
sudo docker logs firebase_deploy
sudo docker ps -a