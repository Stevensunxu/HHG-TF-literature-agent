import requests


def search_semantic():

    papers=[]


    queries=[

        "solid state high harmonic generation",

        "strong field ultrafast physics",

        "optical terahertz emission",

        "light field control solids"

    ]


    current_year=datetime.now().year


    for q in queries:


        try:

            r=requests.get(

                "https://api.semanticscholar.org/graph/v1/paper/search",

                params={

                    "query":q,

                    "limit":10,

                    "year":
                    f"{current_year}-",

                    "fields":
                    "title,abstract,url,venue,year"

                },

                timeout=15

            )


            data=r.json()


        except:

            continue



        for p in data.get("data",[]):


            papers.append({

                "title":
                p.get("title",""),

                "abstract":
                p.get("abstract",""),

                "link":
                p.get("url",""),

                "source":
                p.get("venue","Semantic Scholar"),

                "year":
                p.get("year",current_year)

            })


    return papers
