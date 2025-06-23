
# https://github.com/ChaosDragon01/networking


# Documentation for Server 

The server folder contains all the important files needed to run this local messaging web application server. 

# main file is server.py

the server is contained in the server.py file

the user interface is created inthe templates folder and the static folder. Make sure none of those folders are tampered with if the server.py code is not modified relative to the change in static and templates folder

when loading the server there will be multiple given addresses to access the server. However to my tests, Only one of them works
if you run it test for each address to see which one of your address it works

# Logging in: 
             Logging in without an user-id is impossible. please create a new account which will also be stored locally in the 
             logindata.csv file. The data.csv file is used for storing access get and post request data's it can help identify which process was called and when including which was the IP address used for it 
        Before testing it please make usernames!

# File position
    All the files are carefully positioned, please don't move them unless you plan to change the entire code. 


# Testing it
    When running tests make sure it's done inside another folder. Otherwise new files created might become messy


# testserver.py 

this file most likely won't work beyond opening a port anymore since the file wasn't updated since the html file and it's styles and css were seperated along side that databases were changed and localized

To say simply, don't use it.  



# Libararies
    Flask by python
    & make sure your python libraries are updated fully
    Python library was 3.11.9 64-bit (Microsoft Store) 
