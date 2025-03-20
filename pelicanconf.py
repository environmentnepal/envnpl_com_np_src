AUTHOR = 'environmentnepal'
SITENAME = 'EnvironmentNEPAL'
SITEURL = "https://environmentnepal.com.np"
THEME = "themes/zurb-F5-basic"

PATH = "content"
STATIC_PATHS = ['images', 'static']


TIMEZONE = 'Europe/Rome'

DEFAULT_LANG = 'en'

SUMMARY_MAX_LENGTH = 50  # Optional: Limits auto-generated summaries to 50 words
DEFAULT_METADATA = {'summary': 'No summary available'}


# Feed generation is usually not desired when developing
FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (
    ("Web Archive", "https://web.archive.org/web/20250000000000*/environmentnepal.com.np"),
    ("Pelican", "https://getpelican.com/"),
)

# Social widget
SOCIAL = (

)

DEFAULT_PAGINATION = 10

NEWEST_FIRST_ARCHIVES = True

