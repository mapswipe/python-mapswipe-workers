from mapswipe_workers import mapswipe_workers

only_new_results = False
mapswipe_workers._run_generate_stats(only_new_results)

only_new_results = True
mapswipe_workers._run_generate_stats(only_new_results)
