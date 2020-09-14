# x-elo
Discord bot for tracking ELO rating

# table in DB
CREATE TABLE rating ( id INTERGER PRIMARY KEY, user_id INTEGER UNIQUE NOT NULL, user_name TEXT NOT NULL, rating INT DEFAULT 1500, games INT DEFAULT 0, wins INT DEFAULT 0, losses INT DEFAULT 0, ties INT DEFAULT 0);
# insert new record
insert into rating (user_id, user_name) values (1, 'test');
# result select * from rating;
1|test|1500|0|0|0|0