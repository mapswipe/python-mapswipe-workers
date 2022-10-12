# This Makefile aims to make daily mapswipe admin tasks a bit easier by collecting
# all common commands here, with a simple built-in help system.
# On the command line, just type "make<space><tab>"
#
# prefix all risky commands with "danger_" :)

workers_status:
        docker ps -a

danger_restart_project_creation_worker:
        docker compose up -d mapswipe_workers_creation

make_project_manager:
        @echo "run with email=thing@domain.com to give PM rights"; docker compose run mapswipe_workers_creation mapswipe_workers -v user-management --action=add-manager-rights --email=$(email)
