# Guy.Robot
A discord bot for previewing links to gaming forum
Dependencies: Discord.py, requests, beautifulsoup4
When a user posts a link to a forum post on a supported site the bot will automaticall embed a message previewing the post.
Currently supported sites are neoGAF.com and ResetERA. The bot uses a reaction based interface to allow the user who posted the
link, or admins to maximize, minimize or close the preview. The bot requires a configuration file including the bot's discord token
and some embed parameters to run. 
