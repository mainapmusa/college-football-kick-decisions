'''
NOTES:
Get the Away team ID from the left side of the page header
Get the home team ID from the left side of the page header

Get the ID of the logo from this drive's accordion
  use to know if home or away team
  get the shortened value (STAN vs RICE) from score region on right of accordion

Now know who has the ball and can use that to compare if on own or opponents side of the ball (50 just says 50, neither team)
  if on own side of ball then do not do kick decision
  if beyond 35 do not do kick decision
'''


'''
GetWeeksForYear() -> returns list of weeks to check
for week in weeks:
    Send 'weekly round up for *YEAR* week *WEEK*' tweet
    GetWrongCalls()
        start crawling ESPN
        for each game in this week:
            go to play by play page
            get overall info (home team id, away team id, etc)
            for each drive:
                for each play:
                    if 4th down inside the 35 happened(also maybe if close game and not 4th quarter):
                        get decision and tweet
                        (later find if they chose right decision)
    
'''
