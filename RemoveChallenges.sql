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






