from flask import Flask, Response, request, render_template # type: ignore
from feedgen.feed import FeedGenerator
import feedparser # type: ignore
import pprint

app = Flask(__name__)

# list rss feeds to read from
rss_feeds = {
    "Global News": {
        "Fire Engineering" : ["https://www.fireengineering.com/feed/"],
        "FacilitiesNet" : ["https://www.facilitiesnet.com/rss/msarticles.asp"],
    },

    "Fire Safety": {
        "FireRescue1" : ["https://www.firerescue1.com/news"],

        },
    
    "Local News": {
        "Automatic Fire Engineering (Ireland)" : ["https://automaticfire.ie/news/feed/"],
        "The FPA" : ["https://www.thefpa.co.uk/news/news-archive"],
        "Fire Industry Association" : ["https://www.fia.uk.com/news/blogs.html"],
        "UK Fire" : ["https://ukfiremag.co.uk/news/"],
    },

}

def get_feeds():
    all_news = {}

    for category, sources in rss_feeds.items():
        category_articles = {}

        for source, urls in sources.items():
            articles = []

            for url in urls:
                parsed = feedparser.parse(url)
                articles.extend(parsed.entries[:5]) # top5 entries
            
             # Optional: Sort articles by date if available
            articles = sorted(articles, key=lambda x: x.get("published_parsed", None) or 0, reverse=True)

            category_articles[source] = articles[:5]  # Limit to top 5 per source after merging

        all_news[category] = category_articles

    return all_news

@app.route("/")
def home():
    news = get_feeds()
    pprint.pprint(news) # shows what is being returned
    return render_template("index.html", news=news)

@app.route("/rss.xml")
def rss():
    news = get_feeds()

    fg = FeedGenerator()
    fg.title("Aggregated Fire News Feed")
    fg.link(href=request.host_url, rel='alternate')
    fg.description("Custom RSS feed of fire protection and safety news")
    fg.language('en')

    # loop through all articles and add to feed
    for category, sources in news.items():
        for source, articles in sources.items():
            for entry in articles:
                fe = fg.add_entry()
                fe.title(entry.get('title', 'No Title'))
                fe.link(href=entry.get('link', '#'))
                fe.description(entry.get('summary', 'No Description'))
                if 'published' in entry:
                    fe.pubDate(entry.published)

    
    response = Response(fg.rss_str(pretty=True), mimetype='application/rss+xml')
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
