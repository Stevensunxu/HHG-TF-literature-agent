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

    papers = []

    for keyword in KEYWORDS[:10]:

        url = "https://api.crossref.org/works"

        params = {

            "query.title": keyword,
            "rows": 10,
            "select":
            "title,abstract,DOI,container-title,published"

        }

        try:

            r = requests.get(
                url,
                params=params,
                timeout=15
            )

            data = r.json()

        except Exception:

            continue


        for item in data["message"]["items"]:

            title = item.get(
                "title",
                [""]
            )[0]


            doi = item.get(
                "DOI",
                ""
            )


            journal = item.get(
                "container-title",
                ["Unknown"]
            )[0]


            abstract = item.get(
                "abstract",
                ""
            )


            if title:


                papers.append({

                    "title": title,

                    "abstract": abstract,

                    "link":
                    "https://doi.org/" + doi,

                    "source":
                    journal

                })


    return papers
