import requests


def search_semantic():

    url="https://api.semanticscholar.org/graph/v1/paper/search"


    query="solid state high harmonic generation"


    params={

        "query":query,

        "limit":20,

        "fields":
        "title,abstract,url,year"

    }


    r=requests.get(
        url,
        params=params
    )


    papers=[]


    for p in r.json()["data"]:


        papers.append({

            "title":
            p["title"],

            "abstract":
            p.get(
                "abstract",
                ""
            ),

            "link":
            p.get(
                "url",
                ""
            ),

            "source":
            "Semantic Scholar"

        })


    return papers
