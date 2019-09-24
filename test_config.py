import os
import json


def test_postgres_config():
    file_path = '.env'
    assert os.path.isfile(file_path), \
        f"you didn't set up an environment .env file: {file_path}"

    with open(file_path, 'r') as f:
        env_variables = f.read()

    assert 'POSTGRES_PASSWORD' in env_variables, \
        f"you didn't set a POSTGRES_PASSWORD in {file_path}"

    assert 'WALG_GS_PREFIX' in env_variables, \
        f"you didn't set a WALG_GS_PREFIX in {file_path}"

    file_path = 'postgres/serviceAccountKey.json'
    assert os.path.isfile(file_path), \
        f"you didn't set up an service account key for wal-g and postgrs: {file_path}"


def test_firebase_config():
    file_path = '.env'
    assert os.path.isfile(file_path), \
        f"you didn't set up an environment .env file: {file_path}"

    with open(file_path, 'r') as f:
        env_variables = f.read() # .split('\n')

    assert 'FIREBASE_TOKEN' in env_variables, \
        f"you did not set a firebase token in {file_path}"


def test_mapswipe_workers_service_account():
    # test serviceAccountKey
    file_path = 'mapswipe_workers/config/serviceAccountKey.json'
    assert os.path.isfile(file_path), \
        f"you didn't set up config file: {file_path}"


def test_mapswipe_workers_configuration():
    file_path = 'mapswipe_workers/config/configuration.json'
    assert os.path.isfile(file_path), \
        f"you didn't set up config file: {file_path}"

    with open(file_path, 'r') as f:
        configuration = json.load(f)

    # test postgres config
    assert configuration.get('postgres', None), \
        f"you didn't set postgres config in {file_path}"

    assert configuration.get('postgres', {}).get('host', None), \
        f"you didn't set postgres host in {file_path}"

    assert configuration.get('postgres', {}).get('port', None), \
        f"you didn't set postgres host in {file_path}"

    assert configuration.get('postgres', {}).get('database', None), \
        f"you didn't set postgres database in {file_path}"

    assert configuration.get('postgres', {}).get('username', None), \
        f"you didn't set postgres username in {file_path}"

    assert configuration.get('postgres', {}).get('password', None), \
        f"you didn't set postgres password in {file_path}"

    # test firebase config
    assert configuration.get('firebase', None), \
        f"you didn't set firebase config in {file_path}"

    assert configuration.get('firebase', {}).get('database_name', None), \
        f"you didn't set firebase database_name in {file_path}"

    assert configuration.get('firebase', {}).get('api_key', None), \
        f"you didn't set firebase api_key in {file_path}"

    # test firebase config
    assert configuration.get('firebase', None), \
        f"you didn't set firebase config in {file_path}"

    assert configuration.get('firebase', {}).get('database_name', None), \
        f"you didn't set firebase database_name in {file_path}"

    assert configuration.get('firebase', {}).get('api_key', None), \
        f"you didn't set firebase api_key in {file_path}"

    # test imagery, we test only for bing now
    assert configuration.get('imagery', None), \
        f"you didn't set imagery config in {file_path}"

    assert configuration.get('imagery', {}).get('bing', None), \
        f"you didn't set bing imagery config in {file_path}"

    assert configuration.get('imagery', {}).get('bing', {}).get('url', None), \
        f"you didn't set bing imagery url in {file_path}"

    assert configuration.get('imagery', {}).get('bing', {}).get('api_key', None), \
        f"you didn't set bing imagery api_key in {file_path}"

    # test sentry config
    assert configuration.get('sentry', None), \
        f"you didn't set sentry config in {file_path}"

    assert configuration.get('sentry', {}).get('dsn', None), \
        f"you didn't set sentry dsn value in {file_path}"

    # test slack config
    assert configuration.get('slack', None), \
        f"you didn't set slack config in {file_path}"

    assert configuration.get('slack', {}).get('token', None), \
        f"you didn't set slack token in {file_path}"

    assert configuration.get('slack', {}).get('channel', None), \
        f"you didn't set slack channel in {file_path}"

    assert configuration.get('slack', {}).get('username', None), \
        f"you didn't set slack username in {file_path}"


def test_manager_dashboard_config():
    file_path = 'manager_dashboard/manager_dashboard/js/app.js'
    assert os.path.isfile(file_path), \
        f"you didn't set up config file: {file_path}"

    with open(file_path, 'r') as f:
        app_config = f.read()

    assert 'apiKey' in app_config, \
        f"you didn't set manager_dashboard firebase apiKey in: {file_path}"

    assert 'authDomain' in app_config, \
        f"you didn't set manager_dashboard firebase authDomain in: {file_path}"

    assert 'databaseURL' in app_config, \
        f"you didn't set manager_dashboard firebase databaseURL in: {file_path}"

    assert 'storageBucket' in app_config, \
        f"you didn't set manager_dashboard firebase storageBucket in: {file_path}"


def test_nginx_config():
    file_path = '.env'

    with open(file_path, 'r') as f:
        env_variables = f.read()

    assert 'SERVER_NAME' in env_variables, \
        f"you didn't set a POSTGRES_PASSWORD in {file_path}"

    file_path = 'nginx/nginx.conf'
    assert os.path.isfile(file_path), \
        f"you didn't set up config file: {file_path}"

    with open(file_path, 'r') as f:
        nginx_config = f.read()

    assert 'server_name' in nginx_config, \
        f"you didn't set server_name in: {file_path}"

    # TODO: get server name from nginx config file or .env
    server_name = 'dev.mapswipe.org'

    file_path = f'/etc/letsencrypt/live/{server_name}/fullchain.pem'
    assert os.path.isfile(file_path), \
        f"you didn't set up ssl certificate: {file_path}"

    file_path = f'/etc/letsencrypt/live/{server_name}/privkey.pem'
    assert os.path.isfile(file_path), \
        f"you didn't set up ssl certificate key: {file_path}"


if __name__ == '__main__':
    test_firebase_config()
    test_postgres_config()
    test_mapswipe_workers_service_account()
    test_mapswipe_workers_configuration()
    test_manager_dashboard_config()
    test_nginx_config()
    print("your configuration looks complete. However we didn't test if the values are set correct.")
