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

ALTER TABLE turn ADD turn_score int;
/*UPDATE turn SET SELECT turn_id, COALESCE(lag(p2_score, 1) OVER (PARTITION BY gamenum order by movenum), 0) as prevscore from turn where is_player2 = ' 1';
*/





