 select gamenum from 
 (
 Select gamenum, 
 (Select max(movenum) from turn where length(rack) = 7 and is_player2=' 1' and turn.gamenum = game.gamenum ) as p2_last_7,
 (Select min(movenum) from turn where length(rack) < 7 and is_player2=' 1' and turn.gamenum = game.gamenum) as p2_first_non_7,
 (Select max(movenum) from turn where length(rack) = 7 and is_player2=' 0' and turn.gamenum = game.gamenum ) as p1_last_7,
 (Select min(movenum) from turn where length(rack) < 7 and is_player2=' 0' and turn.gamenum = game.gamenum) as p1_first_non_7 
 
 from game
) g where /*(g.p2_last_7 < p2_first_non_7)*/ 
 (g.p1_last_7 < p1_first_non_7)

 
 
 
 
