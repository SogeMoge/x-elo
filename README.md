# x-elo
Discord bot for tracking ELO rating

# Create DB
sqlite3
.open elo.db
# table in DB
CREATE TABLE rating (member_id INTEGER UNIQUE PRIMARY KEY, member_name TEXT NOT NULL, rating INT DEFAULT 1500, games INT DEFAULT 0, wins INT DEFAULT 0, losses INT DEFAULT 0);
# insert new record
insert into rating (member_id, member_name) values (1, 'test');
# result select * from rating;
1|test|1500|0|0|0

# table for storing game results
CREATE TABLE games (id INTEGER NOT NULL, member_id INTEGER NOT NULL, opponent_id INTEGER NOT NULL, result TEXT NOT NULL, score TEXT NOT NULL, FOREIGN KEY(member_id) REFERENCES rating(member_id), FOREIGN KEY(opponent_id) REFERENCES rating(member_id));

# pipenv
pip3 install -U discord.py
pip3 install -U python-dotenv