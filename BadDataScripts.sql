
/* games I've determined to be bad by inspection */

insert into bad_games select 358;
insert into bad_games select  394;
insert into bad_games select  1079; 
insert into bad_games select  3903;
insert into bad_games select  4876;
insert into bad_games select  4925;
insert into bad_games select  4927;
insert into bad_games select  5117;
insert into bad_games select  5323;
insert into bad_games select  5610;
insert into bad_games select  6905;
insert into bad_games select  6945;
insert into bad_games select  6947;
insert into bad_games select  6992;
insert into bad_games select  7369;
insert into bad_games select  7502;
insert into bad_games select  7701;
insert into bad_games select  7715;
insert into bad_games select  8730;
insert into bad_games select  8854;
insert into bad_games select  9038;
insert into bad_games select  9347;
insert into bad_games select  9456;
insert into bad_games select  9584;
insert into bad_games select  10298;
insert into bad_games select  16713;
insert into bad_games select  16714;
insert into bad_games select  16715;
insert into bad_games select  16727;
insert into bad_games select  16765;
insert into bad_games select 21722;
insert into bad_games select  26950;
insert into bad_games select  29983;
insert into bad_games select 4012;
insert into bad_games select 2550;
insert into bad_games select 6547;

/* games where a player does not score */
insert into bad_games select distinct gamenum from game where gamenum not in (select distinct gamenum from turn where p1_score > 0)
insert into bad_games select distinct gamenum from game where gamenum not in (select distinct gamenum from turn where p2_score > 0)



/* games where final score is 0 */
insert into bad_games SELECT gamenum from game where p2_final_score=0 and gamenum not in (Select * from bad_games)


/* games where total # of tiles played < 85 */
insert into bad_games
select gamenum from (
SELECT gamenum, sum(length(replace(move, '.', ''))) as len_game from turn where not is_challenge and not challenged_away and not is_exchange and gamenum not in (SELECT * from bad_games) 
group by gamenum
)  as bozo where len_game < 85




/* remove games with weird negative scores */
insert into bad_games Select distinct gamenum from turn where turn_score < 0 and NOT is_challenge  and gamenum not in (SELECT * from bad_games)




/* weird 0s at the end of games */ 
DELETE  from  turn where turn_score < 0 and not is_challenge and gamenum not in (SELECT game_num from bad_games) and p1_score=0 and p2_score=0


