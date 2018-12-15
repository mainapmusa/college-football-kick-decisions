
tweetString = "Year: 2018\
Best FG decisions\
1. Notre Dame - @NDFootball @OneFootDown\
+14.48\
2. Nevada - @NevadaFootball @MWCConnection\
+13.25\
3. South Florida - @USFFootball @StampedeSBN\
+12.97\
4. Syracuse - @CuseFootball @NunesMagician\
+12.23\
5. Middle Tennessee - @MTAthletics\
+11.76\
\
#AI #ML #maina #musa #time #for #us #to #go #to #the #party"
print(tweetString.count('\n'))
while(len(tweetString) > 280):
    print(len(tweetString))
    tweetString = tweetString[::-1].split('#',1)[1][::-1]
    print(tweetString)
