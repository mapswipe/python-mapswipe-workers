def parse_geom(geom):
    if geom:
        geom_list = []
        data = geom.split("(")
        new_data = data[1].split(" ")
        lat = float(new_data[0])
        geom_list.append(lat)
        long_des = new_data[1].split(")")
        long = float(long_des[0])
        geom_list.append(long)
        return geom_list
    return geom
