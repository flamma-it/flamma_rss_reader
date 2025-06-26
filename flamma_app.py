from flask import Flask, Response, request, render_template # type: ignore
from feedgen.feed import FeedGenerator
import feedparser # type: ignore
import pprint

app = Flask(__name__)

# list rss feeds to read from
rss_feeds = {
    "Fire Engineering": {
        "Fire Engineering" : ["https://www.fireengineering.com/feed/"],
        "Fire Rescue 1" : ["https://www.firerescue1.com/rss/news/"],
        "FireHouse" : ["https://www.firehouse.com/rss.xml"],
        "NPFA" : ["https://www.npfa.org/news-and-research/"],
        "IFSEC Global - Fire Safety" : ["https://www.ifsecglobal.com/feed/"],
        "Internation Association of Fire Chiefs (IACF)" : ["https://www.iafc.org/docs/default-source/1assoc/news/"],
    },

    "Fire Safety": {
        "UL Fire Safety": ["https://www.ul.com/industries/fire-safety"],
        "FM Global" : ["https://www.fmglobal.com/newsroom"],
        },
    
    "Local News": {
        "ASFP" : ["https://asfp.org.uk/news/?utm_source=chatgpt.com"],
        "Automatic Fire Engineering (Ireland)" : ["https://automaticfire.ie/news/feed/"],
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
                articles.extended(parsed.entries[:5]) # top5 entries
            
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

    # 🛠️ Fix the typo below!
    response = Response(fg.rss_str(pretty=True), mimetype='application/rss+xml')
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)