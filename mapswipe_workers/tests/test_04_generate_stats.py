from mapswipe_workers.generate_stats import generate_stats


if __name__ == '__main__':

    project_id_list = ['change_detection_uganda_planet_wms', 'build_area_default_with_bing']
    generate_stats.generate_stats(project_id_list)
