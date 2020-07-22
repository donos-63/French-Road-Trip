SQL_CREATE_TABLE_PREFECTURE = """
    CREATE TABLE prefecture (insee_code TEXT PRIMARY KEY, 
                            postal_code TEXT,
                            city TEXT, 
                            department TEXT, 
                            region TEXT, 
                            statut TEXT, 
                            average_altitude FLOAT, 
                            area_size FLOAT,
                            population FLOAT, 
                            geo_lat FLOAT, 
                            geo_long FLOAT, 
                            city_code INTEGER, 
                            canton_code INTEGER,
                            district_code INTEGER, 
                            departement_code INTEGER, 
                            area_code INTEGER)
                            """

SQL_CREATE_TABLE_JOURNEY = """
                            CREATE TABLE journey (insee_code_from INTEGER, 
                                                  insee_code_to INTEGER, 
                                                  co2 FLOAT, 
                                                  duration INTEGER)
                            """
#todo : on conflict do update
SQL_INSERT_PREFECTURE = """
                        INSERT 
                        INTO prefecture (insee_code, 
                                        postal_code, 
                                        city, 
                                        department,
                                        region, 
                                        statut, 
                                        average_altitude, 
                                        area_size, 
                                        population, 
                                        geo_lat, 
                                        geo_long, 
                                        city_code, 
                                        canton_code, 
                                        district_code, 
                                        departement_code, 
                                        area_code) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT DO NOTHING 
                        """

SQL_INSERT_WAYPOINT = """
                        INSERT INTO journey (insee_code_from, 
                                             insee_code_to, 
                                             co2, 
                                             duration)
                        VALUES (%s, %s, %s, %s)
                        """

SQL_GET_WAYPOINTS = """
                        SELECT insee_code_from, 
                            insee_code_to, 
                            co2, 
                            duration
                        FROM journey
                    """

SQL_GET_ALL_PREFECTURE = """
                            SELECT insee_code 
                            FROM prefecture
                        """