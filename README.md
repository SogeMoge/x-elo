# x-elo
Discord bot for tracking ELO rating

# Create DB
sqlite3
.open elo.db
# table in DB
CREATE TABLE rating ( id INTERGER PRIMARY KEY, member_id INTEGER UNIQUE NOT NULL, member_name TEXT NOT NULL, rating INT DEFAULT 1500, games INT DEFAULT 0, wins INT DEFAULT 0, losses INT DEFAULT 0, ties INT DEFAULT 0);
# insert new record
insert into rating (member_id, member_name) values (1, 'test');
# result select * from rating;
1|test|1500|0|0|0|0