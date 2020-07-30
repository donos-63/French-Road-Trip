"""
    List of queries used by the application
"""

#Create instructions
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
                            CREATE TABLE journey (insee_code_from TEXT, 
                                                  insee_code_to TEXT, 
                                                  co2 FLOAT, 
                                                  duration INTEGER,
                                                  FOREIGN KEY (insee_code_from) REFERENCES prefecture (insee_code),
												  FOREIGN KEY (insee_code_to) REFERENCES prefecture (insee_code))
                            """

                                                  
SQL_CREATE_TABLE_SUBSTITUTE = """
                            CREATE TABLE substitute (insee_code_original TEXT, 
                                                  insee_code_substitute TEXT)
                            """
                            
SQL_CREATE_TABLE_FRENCH_TRIP = """
                            CREATE TABLE french_trip (
                                                  id SERIAL PRIMARY KEY,
                                                  geo_point_from TEXT, 
                                                  geo_point_to TEXT,
                                                  description TEXT, 
                                                  section_type TEXT, 
                                                  duration INTEGER, 
                                                  co2_emission FLOAT)

                            """

#Insert instructions
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

SQL_INSERT_CITY_WITHOUT_STATION = """
                            INSERT INTO substitute (insee_code_original)
                            VALUES (%s)
                        """

                                                   
SQL_INSERT_FRENCH_TRIP_SECTION = """
                            INSERT INTO french_trip (geo_point_from, geo_point_to, description, section_type, duration, co2_emission)
                            VALUES (%s, %s, %s, %s, %s, %s)
                                """

#Select instructions
SQL_GET_WAYPOINTS = """
                        SELECT insee_code_from, 
                            insee_code_to, 
                            co2, 
                            duration
                        FROM journey
                    """

SQL_GET_ALL_PREFECTURE = """
                            SELECT case when exists (select 1 from substitute where insee_code = insee_code_original) then (select insee_code_substitute from substitute where insee_code = insee_code_original) else insee_code end as insee_code ,
                                    postal_code, 
                                    city, 
                                    geo_lat || ';' || geo_long as geo_point
                            FROM prefecture
                        """

SQL_GET_FRENCH_TRIP_RESUME = """
                            SELECT description, section_type FROM french_trip 
                            ORDER BY id ASC
                                """

SQL_GET_C02_CONSUMPTION_RESUME = """
                                select SUM(duration) duration_total, SUM(co2_emission) co2_total from french_trip
                                """                                

SQL_GET_FRENCH_TRIP = """
                            SELECT split_part(geo_point_from, ';', 1) as long_from,
                                    split_part(geo_point_from, ';', 2) as lat_from,
                                    split_part(geo_point_to, ';', 1) as long_to,
                                    split_part(geo_point_to, ';', 2) as lat_to,
                                    description, 
                                    section_type
                            FROM french_trip
                            WHERE section_type = 'SUB_SECTION'
                            ORDER BY id ASC
                            """                                

#Delete instructions
SQL_REINIT_FRENCH_TRIP = """
                         DELETE FROM french_trip
                        """

SQL_REINIT_JOURNEY = """
                         TRUNCATE TABLE journey
                        """              

SQL_REINIT_PREFECTURE = """
                         DELETE FROM prefecture
                        """                                     
