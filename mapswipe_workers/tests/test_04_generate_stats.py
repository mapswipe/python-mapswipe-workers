from mapswipe_workers.generate_stats import generate_stats


if __name__ == '__main__':
    # TODO: Do we need a mechanism to copy data only for specific users or projects?
    only_new_results = True
    generate_stats(only_new_results)
