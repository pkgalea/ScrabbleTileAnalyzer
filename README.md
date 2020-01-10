

[__Winter 2019/2020 Galvanize Data Science Immersive__](https://www.galvanize.com/austin)

# To B or not to B: Observational study of the relative value of scrabble tiles
<br><br>
An Investigation of how a specific tile on a Scrabble rack changes the score of a Scrabble Turn

__Abstract:__
There have been several studies looking at the value of a given Scrabble tile but these were all computer simulations.  This is an observational study from over 360,000 individual actual scrabble moves as uploaded to Cross-Tables.com.  The goal is answer the question "How many more (or less) points will a given tile lead to on a given turn of scrabble?".  I have built a flask app to allow users to explore this on their own.


__Results:__
Because the sample size is so large there were many of significant results.  Individual Z-tests for certain tiles can be found by running the flask App:  

http://3.14.64.250/

One example:  Racks with a Q were found to score between [4.41, 5.03] less points.



See this work as a presentation in [Google Slides]
---

# Background & Motivation
As an amateur scabble player I have an intuitive sense of the relative value of tiles.  I love the blanks and the X.  I hate the U's and the V's.   The motivation behind this study is to see if my intuitions match the quantitative results.

# Hypotheses

To Fill in later

# Analysis methods

The tech stack consists of MongoDb, Beautiful Soup, Python 3, Numpy, Pandas, Matplotlib, HTML, Postgres SQL, Flask, Amazon EC2, SciPy, Ngnix and Docker.


The data was scraped from https://www.cross-tables.com/annolistself.php.  These are self uploaded, complete Scrabble games.  Many of these games come from major tournaments.  

# Confounding Factors

To fill in later.

Counfounding factors include: Player Rating, Turn Number, Dictionary, Board Layout.

![confounders](http://github.com/pkgalea/scrabble/images/confounders.png)



# Data

Data was scraped from https://www.cross-tables.com/annolistself.php  It consisted of 36K games and 800K turns.  Incomplete games and fake games were removed.

# Future Analysis

There is so much more that could be done.  

I would love to look at how much each turn affects your final score in the game.  This is more complicated as you need to account for the tiles given.  When you look at this you find that every tile has a positive effect!  This is because of the general trend of more tiles=more points.  I would like to look at the expected distribution


# Acknowledgements

Thanks to Joseph Gartner, Dan Rupp & Brent Goldberg for their help and guidance during this project.


# References


# Web App


http://3.14.64.250/

