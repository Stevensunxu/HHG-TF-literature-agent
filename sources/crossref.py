import requests


KEYWORDS = [

"high harmonic generation",

"solid state HHG",

"strong field physics",

"terahertz emission",

"ultrafast carrier dynamics",

"light field control"

]


def search_crossref():

    papers=[]


    for keyword in KEYWORDS:


        url="https://api.crossref.org/works"


        params={

            "query.title":keyword,

            "rows":10,

            "filter":
            "from-pub-date:2026-01-01"

        }


        r=requests.get(
            url,
            params=params
        )


        data=r.json()


        for item in data["message"]["items"]:


            title=item.get(
                "title",
                ["Unknown"]
            )[0]


            doi=item.get(
                "DOI",
                ""
            )


            papers.append({

                "title":title,

                "link":
                "https://doi.org/"+doi,

                "source":
                "Crossref",

                "abstract":
                item.get(
                    "abstract",
                    ""
                )

            })


    return papers
