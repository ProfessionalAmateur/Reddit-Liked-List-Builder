Reddit Liked List Builder
=========================

Overview
--------
As a frequent Reddit user I find a lot of good new music browsing the [electronic music subreddit](http://www.reddit.com/r/electronicmusic) but never had a good way to keep track of it.  Wanting to relisten to a song I had previously liked I needed to browse through my liked history.  However after a week or two any link I upvoted would be buried several pages deep, proving to be kind of a hassle.  

The Reddit Liked Link Builder solves the problem of needing to manually search.  This script will parse a users 'liked' history for a given subreddit and output a list of HTML links to a file.  In its current state the Reddit link must have "media": data associated with it.  This was done to prevent 'self' posts or regular article from appearing in the list.

Usage
-----
1) Download the redditlikedlist.py and rll.cfg to a directory of your choice.  
2) Populate the following fields in the rll.cfg file:

    [PATHS]  
    outputfile = The destination of the output file.  Example: /home/John/musiclist.HTML  
    subreddit = The subreddit you want to parse from.  Example: electronicmusic  
    
    [WAYPOINT]  
    beforelinkname = (leave blank, the script will populate)  
    
    [CREDENTIALS]  
    username = Your Reddit username, must have a valid Reddit account to use this script.  
    password = Your Reddit password, must have a valid Reddit account to use this script.  
    useragent = Reddit requires a unique user agent for all calls to its API, it is recommended  
                you incorporate your username in the agent.  Example: BobaFett37's Liked List Parse  
    
    [OUTPUT]  
    format = (embeded|standard) The standard format will create a list of HTML href links.  
             The embeded format will create youtube and soundcloud embeded html in collapsible divs.  
             Prereqs for using embeded:  
             1) jQuery  
             2) Collapsible jQuery plugin - https://github.com/juven14/Collapsible  
             3) While not required the css file, and images will add some a nice touch to  
                the collapsible/expandible div's.   


3) Run the python script passing the configuration file location as a parameter:

    $> python redditlikedlist.py rll.cfg

The first time the script is run it will start with your most recent liked links and work backwards into the past.  Reddit will allow you to parse your most recent 1000 links.  After the first run the script stores the most recent link in the 'beforelinkname' in the configuration file.  Subsequent executions the script will start parsing from this link and work forward to present time.

Output
------

The HTML file output will contain the last processed date stamp as well as a list of HTML links to media content.  Example:

**Standard Output Sample**

    Last updated at: 2013-09-20 07:00:07<br/><br/>
    <a href='http://www.youtube.com/watch?v=XXXXXXXXXXX'>Music Video 1</a><br/>
    <a href='http://www.youtube.com/watch?v=XXXXXXXXXXX'>Music Video 2</a><br/>
    <a href='http://www.youtube.com/watch?v=XXXXXXXXXXX'>Music Video 3</a><br/>
    <a href='http://www.youtube.com/watch?v=XXXXXXXXXXX'>Music Video 4</a><br/>
    <a href='http://www.youtube.com/watch?v=XXXXXXXXXXX'>Music Video 5</a><br/>

**Embeded Output Sample**

    <div class='collapsible'>
       <a href='http://www.youtube.com/watch?v=XXXXXXXXX'>Song 1 - Artist1</a><span></span>
    </div>
    <div class='container'>
       <div class='content'>
          <div>
             <iframe width='420' height='315' src='//www.youtube.com/embed/XXXXXXXXXX' frameborder='0' allowfullscreen></iframe>
          </div>
       </div>
    </div>
    <div class='collapsible'>
       <a href='https://soundcloud.com/ARTIST/SONG>Song 2 - Artist 2</a><span></span>
    </div>
    <div class='container'>
       <div class='content'>
          <div>
             <iframe width="100%" height="166" scrolling="no" frameborder="no" src="https://w.soundcloud.com/player/?url=http%3A%2F%2Fapi.soundcloud.com%2Ftracks%XXXXXXXXXX&show_artwork=true"></iframe>
          </div>
       </div>
    </div>


To-do wishlist
---------------
- Validate Youtube links are still valid (i.e. not pulled by record labels or deleted by YouTube poster)
- Incorporate more than 1 subreddit to parse in config file.
- Add list sorting
