import patternGen
import flask
from patternGen.src.pattern_gen import PatternGen
import pandas as pd
import random
import os

@patternGen.app.route('/', methods=["GET", "POST"])
def show_index():
    if flask.request.method == "POST":
        players = flask.request.form.get("players")
        beats = flask.request.form.get("beats")

        if not players.isdigit() or not beats.isdigit():
            error = "Please enter valid numeric values for players and beats."
            return flask.render_template("index.html", error=error)

        players = int(players)
        beats = int(beats)
        pg = PatternGen(players, beats)

        context = {"pattern": pg}
        pattern = pg.generate_pattern()
        name = generate_name()
        df = pattern.to_df()

        node_positions = None
        graphs = []
        for beat in range(beats):
            html, node_positions = pattern.get_beat_image(beat, node_positions)
            graphs.append((html, beat))
        

        context = {"table_html": df.to_html(index=False), "graphs": graphs, "pattern_name": name}

        return flask.render_template("index.html", **context)
    
    return flask.render_template("index.html")


def generate_name():
    static_dir = os.path.join(patternGen.app.root_path, 'static') 
    # Construct the full path to the CSV file
    baby_csv_path = os.path.join(static_dir, 'Baby Names.csv')
    nouns_csv_path = os.path.join(static_dir, 'Most Common English Nouns.csv')
    names_table = pd.read_csv(baby_csv_path)
    nouns_table = pd.read_csv(nouns_csv_path)
    names = names_table["name"]
    name = random.choice(names)
    nouns = nouns_table["Word"]
    noun = random.choice(nouns)
    return name + "'s " + noun