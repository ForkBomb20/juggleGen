#!/Users/nathan/Development/Visual_Studio/Python/juggling/.juggle/bin/python3
"""Generate juggling passing pattern programatically."""
import click
import random
import pandas as pd
import networkx as nx
from pyvis.network import Network

def validate_non_positive_integer(ctx, param, value):
    try:
        value = int(value)
        if value <= 0:
            raise click.BadParameter(f"{param.name} must be a positive integer.")
        return value
    except ValueError:
        raise click.BadParameter(f"{param.name} must be an integer.")


# ------------ START PATTERN CLASS ------------ #
class Pattern:
    def __init__(self, num_players, num_beats):
        self.pattern = [{i : i for i in range(1, num_players + 1)} for _ in range(num_beats)]

    def set_pass(self, beat_num, pass_mapping):
        self.pattern[beat_num][list(pass_mapping.keys())[0]] = list(pass_mapping.values())[0]

    def __str__(self):
        out = ""
        for beat in self.pattern:
            out += str(beat) + "\n"
        return out
    
    def to_df(self):
        df_rows = {}
        num_keys = len(self.pattern[0])

        for i in range(num_keys):
            player_letter = chr(65 + i)
            throws = []
            for beat in self.pattern:
                throws.append(chr(65 + beat[i + 1] - 1))
            df_rows[player_letter] = throws

        df = pd.DataFrame(df_rows)

        # Transpose and reset index to match the desired format
        df = df.T.reset_index()

        # Rename the columns: 'index' becomes 'Row', and others are numbered from 1
        df.columns = ['Player'] + list(range(1, len(df.columns)))

        return df

    def get_beat_image(self, beat, node_positions=None):
        """
        Generate an HTML-friendly image of a directed graph with consistent node positions.
        """
        G = nx.DiGraph()

        # Populate the graph with edges
        for src, dest in self.pattern[beat].items():
            G.add_node(src, label=chr(65 + src - 1))
            G.add_node(dest, label=chr(65 + dest - 1))
            G.add_edge(src, dest)

        # Predefine or use provided node positions
        if node_positions is None:
            # Generate positions only once based on a circular layout
            node_positions = nx.circular_layout(G)

        # Apply the fixed positions to the graph
        for node in G.nodes():
            if node not in node_positions:
                node_positions[node] = (0, 0)  # Default position for any new nodes

        # Create a PyVis Network object
        net = Network('250px', '250px', notebook=True, directed=True)
        net.from_nx(G)

        # Disable physics for consistent positioning
        for node in net.nodes:
            node.update({'physics': False})
            # Update node positions to match predefined positions
            node_id = node['id']
            if node_id in node_positions:
                x, y = node_positions[node_id]
                node.update({'x': x * 100, 'y': y * 100})  # Scale positions for better display

        # Return the HTML content directly
        return net.generate_html(), node_positions
        
# ------------ END PATTERN CLASS ------------ #


# ------------ START PATTERN GEN CLASS ------------ #
class PatternGen:
    def __init__(self, num_players, num_beats):
        self.players = num_players
        self.beats = num_beats

    def generate_pattern(self):
        # Instantiate a new pattern
        pattern = Pattern(self.players, self.beats)

        # Create one beat at a time
        for beat in range(self.beats):
            # Determine cycles within pattern
            subsets = []
            while sum(subsets) < self.players:
                subsets.append(random.randint(1, self.players - sum(subsets)))
            # Shuffle cycle sizes because otherwise slight bias toward beginnign players having large cycles
            random.shuffle(subsets)

            # Generate beat map from cycles
            start = 0
            for subset_size in subsets:
                players = [start + 1 + i for i in range(subset_size)]
                for i in range(len(players)):
                    pass_mapping = {players[i] : players[(i + 1) % len(players)]}
                    pattern.set_pass(beat, pass_mapping)
                start += subset_size

        return pattern




# ------------ END PATTERN GEN CLASS ------------ #

# @click.command(help="Juggling pattern generator.")
# @click.option(
#     '-p',
#     '--players',
#     required=True,
#     type=int,
#     callback=validate_non_positive_integer,
#     help="Number of players (positive integer)."
# )
# @click.option(
#     '-b',
#     '--beats',
#     required=True,
#     type=int,
#     callback=validate_non_positive_integer,
#     help="Number of beats (positive integer)."
# )
# def main(players, beats):
#     click.echo(f"Number of players: {players}")
#     click.echo(f"Number of beats: {beats}")

#     pg = PatternGen(players, beats)
#     print(pg.generate_pattern())
#     print(pg.generate_name())

# if __name__ == "__main__":
#     main()
