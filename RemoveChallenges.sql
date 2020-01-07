/*
UPDATE turn SET challenged_away = FALSE;
UPDATE turn set challenged_away = TRUE where turn_id in (Select lag_turn_id from (
    SELECT move, turn_id, LAG (turn_id, 1)  OVER (PARTITION BY gamenum ORDER BY movenum) as lag_turn_id  from turn) as sub where move like '-chl-%') ;
UPDATE turn SET is_challenge = FALSE;
UPDATE turn SET is_challenge = TRUE where move like '-chl-%';
UPDATE turn SET is_exchange = FALSE;
UPDATE turn SET is_exchange = TRUE WHERE move = '---';


UPDATE game set p1_final_score = p1_score, p2_final_score = p2_score from turn inner join (select gamenum, max(movenum) as max_movenum from turn where p1_score != 0 and p2_score != 0
 group by gamenum) M on M.gamenum = turn.gamenum and M.max_movenum = turn.movenum WHERE game.gamenum = turn.gamenum
*/


DROP VIEW player2scoreView;
CREATE VIEW player2scoreView as SELECT turn_id, COALESCE(lag(p2_score, 1) OVER (PARTITION BY gamenum order by movenum), 0) as prevscore, p2_score, challenged_away from turn where is_player2 = ' 1';
UPDATE turn SET turn_score = (CASE WHEN t.challenged_away THEN 0 ELSE t.p2_score - t.prevscore end) FROM player2scoreView t where turn.turn_id = t.turn_id;

DROP VIEW player1scoreView;
CREATE VIEW player1scoreView as SELECT turn_id, COALESCE(lag(p1_score, 1) OVER (PARTITION BY gamenum order by movenum), 0) as prevscore, p1_score,challenged_away from turn where is_player2 = ' 0';
UPDATE turn SET turn_score = (CASE WHEN t.challenged_away THEN 0 ELSE t.p1_score - t.prevscore end)  FROM player1scoreView t where turn.turn_id = t.turn_id;

/*
insert into bad_games select 358;
; insert into bad_games select  394; insert into bad_games select  1079; insert into bad_games select  3903; insert into bad_games select  4876; insert into bad_games select  4925; insert into bad_games select  4927; insert into bad_games select  5117; insert into bad_games select  5323; insert into bad_games select  5610; insert into bad_games select  6905; insert into bad_games select  6945; insert into bad_games select  6947; insert into bad_games select  6992; insert into bad_games select  7369; insert into bad_games select  7502; insert into bad_games select  7701; insert into bad_games select  7715; insert into bad_games select  8730; insert into bad_games select  8854; insert into bad_games select  9038; insert into bad_games select  9347; insert into bad_games select  9456; insert into bad_games select  9584; insert into bad_games select  10298; insert into bad_games select  16713; insert into bad_games select  16714; insert into bad_games select  16715; insert into bad_games select  16727; insert into bad_games select  16765; insert into bad_games select 
21722; insert into bad_games select  26950; insert into bad_games select  29983;
insert into bad_games select 4012;
*/






