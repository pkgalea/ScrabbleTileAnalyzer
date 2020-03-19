

[__Winter 2019/2020 Galvanize Data Science Immersive__](https://www.galvanize.com/austin)

# To B or not to B: Observational study of the relative value of scrabble tiles
<br><br>
An Investigation of how a specific tile on a Scrabble rack changes the score of a Scrabble Turn

__Abstract:__
There have been several studies looking at the value of a given Scrabble tile but these were all computer simulations.  This is an observational study from over 360,000 individual actual scrabble moves as uploaded to Cross-Tables.com.  The goal is answer the question "How many more (or less) points will a given tile lead to on a given turn of scrabble?".  I have built a flask app to allow users to explore this on their own.

To explore this tool please see my flask app at: http://18.218.61.61:5000


__Results:__
Because the sample size is so large there were many of significant results.  Individual Z-tests for certain tiles can be found by running the Flask App.  

One example:  Racks with a Q were found to score between [4.41, 5.03] less points as opposed to racks without a Q.

---

# Background & Motivation
As an amateur scabble player I have an intuitive sense of the relative value of tiles.  I love the blanks and the X.  I hate the U's and the V's.   The motivation behind this study is to see if my intuitions match the quantitative results.


# Hypotheses

The hypothesis is that for any given two tiles, having one tile on the rack will result in a different mean score than having a different tile on the rack.

Example.  
Consider two groups:  Control - Racks with a Q on them.   Alternative - Racks with an F on them.

H0:  The mean score of these two groups is the same
Ha:  The mean score of these two groups is different

# Tools Used
The tech stack consists of MongoDb, Beautiful Soup, Python 3, Numpy, Pandas, Matplotlib, HTML, Postgres SQL, Flask, Amazon EC2, Amazon s3, SciPy, Ngnix and Docker.

# Data

Data was scraped from https://www.cross-tables.com/annolistself.php  It consisted of 36K games and 800K turns.  Incomplete games and fake games were removed.  Also, I only consider turns there are 7 letters on the rack and the rack is visible.  This limited the analysis to 360K records.

# Statistical Test

The statistical test is a z-test for the difference of means between the two groups.  The sample sizes are usually very large, so the central limit theorem can be used to assume the distribution for the means is normal.

# Confounding Factors

There are a myriad of other factors to consider.  

Counfounding factors include: Player Rating, Turn Number, Dictionary, Board Layout.

![confounders](https://github.com/pkgalea/scrabble/blob/master/images/confounders.png)

One confounding factor is player ranking.  Not too surprisingly, higher ranked players have higher turn scores.  It might be tempting to think that this won't matter because the tiles are chosen randomly.  However, better players tend to play longer words, so they get more tiles.  And therefore, they'll have a higher chance of having a given tile.  So it would be interesting to control ://for rank in the experiment.

Another counfounding factor is turn number.  You can see that the first few turns tend to score less.  This is liekly due to the lack of bonus squares in the beginning of the game and also that player's "build their rack".  That is, they keep good tiles on their rack to score higher later.  This would also be interesting to control.

Yet another counfounding factor is the dictionary used.  Hasbro recently added "QI" and "ZA" to the dictionarly, allowing for high scoring two-letter Q and Z words.  The effect of the dictionary should be considered.


# Flask App



# Future Analysis

There is so much more that could be done.  

I would love to look at how much each turn affects your final score in the game.  This is more complicated as you need to account for the tiles given.  When you look at this you find that every tile has a positive effect!  This is because of the general trend of more tiles=more points.  I would like to look at the expected distribution


# Acknowledgements

Thanks to Joseph Gartner, Dan Rupp & Brent Goldberg for their help and guidance during this project.


# References


# Web App

Coming soon.

