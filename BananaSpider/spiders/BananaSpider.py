import scrapy
from bs4 import BeautifulSoup


class BananaSpider(scrapy.Spider):
    name = "gasy_prompts"

    def start_requests(self):
        urls = [
            'https://mg.wikipedia.org/wiki/Quissac,_Lot',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        page = response.url

        for p_tag in response.xpath('//*[@id="mw-content-text"]/div/p').getall(): # get all specific p tags that we want
            soup = BeautifulSoup(str(p_tag), features="lxml") # convert to soup object
            try:
                soup.span.decompose() # remove span tags
            except:
                pass
            text = BeautifulSoup.get_text(soup) # get only the text

            # cleaning up the text 
            text = text.replace("\n", "")
            for c in range(len(text)):
                try:
                    # replace decimals
                    if text[c] == ".":
                        if text[c-1].isnumeric() and text[c+1].isnumeric():
                            text = text[:c] + "isadecimal" + text[c+1:]
                    # remove round brackets
                    square_end = 1
                    if text[c] == "(":
                        while text[c+square_end] != ")":
                            square_end += 1
                        text = text[:c-1] + text[c+square_end+1:]
                    # remove square brackets
                    if text[c] == "[" and text[c+1].isnumeric() and text[c+2] == "]":
                        text = text[:c] + text[c+3:]
                except IndexError:
                    pass

            # splitting into sentences
            sentences = text.split(".")

            # append sentences to .jl file
            for s in sentences:
                if s != "\n" and s != "" and s != "." and s != " " and len(s) > 7 and s.count("-") < 2:
                    s = s.replace("isadecimal", ".") # replacing decimals mistaken as periods
                    # get rid of any sentence with a number in it
                    numbers = False
                    for char in s:
                        if char.isnumeric():
                            numbers = True
                    if numbers == False and s[:11] != "Firenena ao" and s[-1] != ":":
                        while s[0] == " ":
                            s = s[1:] # get rid of blank spaces at the start of sentences
                        s = s + "."
                        yield {
                            'URL' : page,
                            'Sentence' : s
                        }
                        with open("prompts.txt", "a") as f:
                            s = s.encode("utf-8").decode("utf-8")
                            s = s + "\n"
                            f.write(s)

        # get links to other malagasy wiki pages
        links = ["https://mg.wikipedia.org/" + link for link in response.xpath('//*[@id="mw-content-text"]/div/p/a/@href').getall() if link[:5] == "/wiki"]
        for link in links:
            if link is not None:
                yield response.follow(link, callback=self.parse)