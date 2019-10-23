from mapswipe_workers.generate_stats import project_stats

project_id = '6'
project_stats = project_stats.get_per_project_statistics(project_id)
print(project_stats)
