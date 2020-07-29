import os
import sys
from bottle import Bottle, run, request, template, debug, static_file
from visualization import MAP_FILE_PATH
from DatabaseAccess.Connector import Connector
import DatabaseAccess.sql_requests as sql
import bdd_management

DIRNAME = os.path.dirname(sys.argv[0])
db_connector = Connector()

app = Bottle()
debug(True)


@app.route('/static/<filename:re:.*\.css>')
def send_css(filename):
    return static_file(filename, root=DIRNAME+'/static/asset/css')


@app.route('/static/<filename:re:.*\.js>')
def send_js(filename):
    return static_file(filename, root=DIRNAME+'/static/asset/js')


@app.route('/images/<filename:re:.*\.png>')
def images(filename):
    return static_file(filename, root=DIRNAME+'/images')


@app.route('/')
def index():
    return template('index', prefectures_table_state="Chargé", journey_table_state="Ok",
                    french_trip_table_state="Calculé")


# """
# Nombre de chansons par artiste
# """
# @app.route('/nbr_artist')
# def nombre_album_par_artist():

#     result = req.get_nbr_chanson_par_artist()

#     output = template('nbr_artist', rows=result)
#     return output

# """
# Durée moyenne des morceaux
# """
# @app.route('/tps_moyen_morceaux')
# def tps_moyen_morceaux():

#     result = req.get_tps_moyen_des_morceaux()

#     output = template('tps_moyen_morceaux', tps=result)
#     return output

# """
# Nombre de morceaux par bpm
# """
# @app.route('/bpm')
# def nombre_titres_par_bpm():

#     result = req.get_nbr_titres_par_bpm()

#     output = template('bpm', rows = result)
#     return output

# """
# Nombre de morceaux qui sont dans plusieurs playlists
# """
# @app.route('/multiplaylists')
# def nombre_de_titres_multiplaylists():

#     result = req.get_nbr_titres_multiplaylists()
#     nbtitres = len(result)

#     output = template('multiplaylists', count = nbtitres, rows = result)
#     return output

# @app.route('/energie_intensite')
# def relation_energie_intensite():
#     """Analyser et afficher la relation entre l’énergie et l’intensité """
#     result = req.get_relation_energie_intensite()

#     output = template('energie_intensite', resultat = result)
#     return output

# @app.get('/load_data')
# def load_data():

#     db_creation = db.create_database()
#     extract = data_extract.extract_data()
#     message = "%s and %s" % (db_creation, extract)

#     return template('index', data = message)

@app.route('/roadtrip_map')
def serve_picture():
    """ return map generated by road trip """
    if not os.path.exists(MAP_FILE_PATH):
        return
    filename = os.path.basename(MAP_FILE_PATH)
    return static_file(filename, root=MAP_FILE_PATH.replace(filename, ''))

@app.route('/consult', method='GET')
def cover_descriptor():
    trip_results = db_connector.execute_query(sql.SQL_GET_FRENCH_TRIP_RESUME)

    return template("consult", trip_results=trip_results)

@app.route('/manage/truncate/<table_name>', method='GET')
def bdd_management(table_name):
    if(table_name == 'journey'):
        bdd_management.truncate_journey()
    if(table_name == 'prefecture'):
        bdd_management.truncate_prefecture()
    if(table_name == 'roadtrip'):
        bdd_management.truncate_roadtrip()

    return template("manage")

@app.route('/manage/fill_prefectures', method='GET')
def bdd_management():
    bdd_management.load_prefecture()

    return template("manage")


# @app.route('/get/prediction/picture/<graph>')
# def serve_data(graph):

# 	return static_file(graph +'.png', root=os.path.dirname(sys.argv[0])+'/images')

# @app.route('/popularity_farida', method='GET')
# def popularity_farida():
#     graphs, predictions, error = req6.compute_prediction()
#     return template("popularity_farida", graphs = graphs, predictions = predictions, error = error)


# @app.route('/popularity_xgb', method='GET')
# def popularity_xgb():
#     """  predict popularity of a song based on songs in a playlist """
#     song = request.query.song
#     playlist = request.query.playlist

#     playlists = get_playlists(playlist)

#     error = ''
#     min= 0
#     max= 0
#     if song != '' and playlist != ''  :
#         try:
#             min, max = xgbModule.get_prediction(song, playlist)
#         except Exception as exception:
#             error = exception.args[0]
#             print('The xgbModule.get_prediction failed')

#     return template('popularity_xgboost',
#     playlists = playlists,
#     errorMessage = error,
#     prediction_min= min,
#     prediction_max= max,
#     song = song)


"""
Run server
"""
run(app, host='localhost', port=8080)
