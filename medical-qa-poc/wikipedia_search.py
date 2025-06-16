# wikipedia_search.py

import wikipedia

class WikipediaSearcher:
    def __init__(self):
        wikipedia.set_lang("en")

    def search_and_summarize(self, query: str) -> str:
        try:
            search_results = wikipedia.search(query)
            if not search_results:
                return ""

            # Take the first search result
            page_title = search_results[0]
            page = wikipedia.page(page_title)
            summary = wikipedia.summary(page_title, sentences=2)

            return f"**Wikipedia - {page_title}**\n\n{summary}"
        except Exception as e:
            print(f"Error in Wikipedia search: {e}")
            return ""
