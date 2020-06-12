from mapswipe_workers.utils.slack_helper import send_progress_notification


project_ids = ["build_area_default_with_bing"]
[send_progress_notification(project_id) for project_id in project_ids]
