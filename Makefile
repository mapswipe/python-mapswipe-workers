# This Makefile aims to make daily admin tasks a bit easier by collecting
# all common commands here, with a simple built-in help system.
# On the command line, just type "make<space><tab>"

workers_status:
	docker ps -a

restart_project_creation_worker:
	docker compose up -d mapswipe_workers_creation

start_all_workers:
	docker compose up -d postgres manager_dashboard nginx api mapswipe_workers_creation mapswipe_workers_stats mapswipe_workers_firebase_to_postgres

stop_all_workers:
	docker compose stop

make_project_manager:
	@echo "run with email=thing@domain.com to give PM rights"; docker compose run --rm mapswipe_workers_creation mapswipe_workers -v user-management --action=add-manager-rights --email=$(email)

remove_project_manager:
	@echo "run with email=thing@domain.com to remove PM rights"; docker compose run --rm mapswipe_workers_creation mapswipe_workers -v user-management --action=remove-manager-right --email=$(email)

update_firebase_functions_and_db_rules:
	docker compose run --rm firebase_deploy

deploy_latest_workers_version:
	git pull; docker compose build postgres django django-schedule-task manager_dashboard community_dashboard nginx api mapswipe_workers_creation mapswipe_workers_stats mapswipe_workers_firebase_to_postgres firebase_deploy; docker compose up -d postgres django django-schedule-task manager_dashboard community_dashboard nginx api mapswipe_workers_creation mapswipe_workers_stats mapswipe_workers_firebase_to_postgres firebase_deploy
