An instagram-parser 

How to use:

	1.Clone or Download it and install requirements.txt
	2.In the folder "instagram_parser_2020" open hashtags_to_parse.txt
	- and put there your links to instagram hashtags pages
	3.In your command line navigate to "instagram_parser_2020" folder and type: scrapy crawl hashtag_spider_1 
	- wait for [scrapy.core.engine] INFO: Closing spider (finished) message
	- check instagram_parser_2020/results/"your hashtag name"/"your hashtag filename.csv"
	4.To Get profiles from scraped hashtags run command: scrapy crawl user_profile_spider_1
	- wait for [scrapy.core.engine] INFO: Closing spider (finished) message
	- check instagram_parser_2020/results/"your hashtag name"/profiles/"your hashtag filename.csv"
	
	P.S: Don't forget about instagram limit ~200 requests per hour.
