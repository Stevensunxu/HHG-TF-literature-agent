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


    today=datetime.now()

    week_ago=today-timedelta(days=7)


    from_date=week_ago.strftime("%Y-%m-%d")

    until_date=today.strftime("%Y-%m-%d")


    for keyword in KEYWORDS[:10]:


        try:

            r=requests.get(

                "https://api.crossref.org/works",

                params={

                    "query.title": keyword,

                    "rows":20,

                    "filter":
                    f"from-pub-date:{from_date},until-pub-date:{until_date}",

                    "sort":
                    "published",

                    "order":
                    "desc"

                },

                timeout=20

            )


            data=r.json()


        except Exception as e:

            print(
                "Crossref error:",
                e
            )

            continue



        for item in data["message"]["items"]:


            title=item.get(
                "title",
                [""]
            )[0]


            if not title:
                continue



            journal=item.get(
                "container-title",
                ["Unknown"]
            )[0]


            doi=item.get(
                "DOI",
                ""
            )


            abstract=item.get(
                "abstract",
                ""
            )



            papers.append({

                "title":title,

                "abstract":abstract,

                "link":
                "https://doi.org/"+doi,

                "source":
                journal,


                "date":
                item.get(
                    "published",
                    {}
                )

            })


    return papers
