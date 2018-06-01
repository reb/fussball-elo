from flask import Flask, request, render_template
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
from sqlalchemy import create_engine, select
from sqlalchemy import Table, Column, Integer, String, MetaData
import operator
import sys

# Create a engine for connecting to SQLite3.
db = create_engine('sqlite:///fussball.db')

metadata = MetaData()
players = Table('players', metadata,
                Column('name', String),
                Column('rating', Integer),
                )

matches = Table('matches', metadata,
                Column('a_off', String),
                Column('a_def', String),
                Column('a_score', Integer),
                Column('b_off', String),
                Column('b_def', String),
                Column('b_score', Integer),
                )

metadata.create_all(db)

app = Flask(__name__)
api = Api(app)
CORS(app)


class Matches(Resource):
    def get(self):
        conn = db.connect()
        s = select([matches])
        result = conn.execute(s)
        return {'matches': [dict(row) for row in result]}

    post_parser = reqparse.RequestParser()
    post_parser.add_argument('a_off', required=True)
    post_parser.add_argument('a_def', required=True)
    post_parser.add_argument('a_score', required=True)
    post_parser.add_argument('b_off', required=True)
    post_parser.add_argument('b_def', required=True)
    post_parser.add_argument('b_score', required=True)

    def post(self):
        conn = db.connect()
        args = self.post_parser.parse_args()
        ins = matches.insert().values(**args)
        result = conn.execute(ins)
        return {'result': dict(result)}


class Ratings(Resource):
    def rating(self, player):
        try:
            return self.ratings[player]
        except KeyError:
            self.ratings[player] = 1200
            return self.ratings[player]

    def tag(self, player_name):
        name_tag = "{} ({})"
        return name_tag.format(player_name, self.ratings[player_name])

    def get(self):
        conn = db.connect()
        s = select([matches])
        result = conn.execute(s)

        self.ratings = {}

        for match in result:
            a_off = match['a_off']
            a_def = match['a_def']
            a_score = match['a_score']
            b_off = match['b_off']
            b_def = match['b_def']
            b_score = match['b_score']

            team_a = self.rating(a_off) + self.rating(a_def)
            team_b = self.rating(b_off) + self.rating(b_def)

            e_a = 1 / (1 + 10 ** ((team_b - team_a)/400.0))
            e_b = 1 / (1 + 10 ** ((team_a - team_b)/400.0))

            r_a = a_score / float(a_score + b_score)
            r_b = b_score / float(a_score + b_score)

            diff_a = int(round(32 * (r_a - e_a)))
            diff_b = int(round(32 * (r_b - e_b)))

            team_tag = "{} & {}"
            team_a_tag = team_tag.format(self.tag(a_off), self.tag(a_def))
            team_b_tag = team_tag.format(self.tag(b_off), self.tag(b_def))
            print("{} vs {}".format(team_a_tag, team_b_tag))
            print("Chance to win: {} vs {}".format(e_a, e_b))
            print("Actual result: {}-{}".format(a_score, b_score))
            print("Actual distribution: {} vs {}".format(r_a, r_b))
            print("Adjusting {} and {}".format(diff_a, diff_b))

            self.ratings[a_off] += diff_a
            self.ratings[a_def] += diff_a
            self.ratings[b_off] += diff_b
            self.ratings[b_def] += diff_b

            new_ratings_tags = [
                self.tag(a_off),
                self.tag(a_def),
                self.tag(b_off),
                self.tag(b_def),
            ]
            print("New Ratings: {}, {}, {}, {}.".format(*new_ratings_tags))

        return self.ratings


api.add_resource(Players, '/players')
api.add_resource(Matches, '/matches')
api.add_resource(Ratings, '/ratings')


@app.route("/")
def home():
    r = Ratings()
    ratings = r.get()

    items = ratings.items()
    key = operator.itemgetter(1)
    sorted_ratings = sorted(items, key=key, reverse=True)

    return render_template('home.html', ratings=sorted_ratings)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(sys.argv[1]))
