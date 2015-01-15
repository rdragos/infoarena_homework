from pyquery import PyQuery as pq
import requests
import logging

logger = logging.getLogger(__name__)
class Infoarena(object):

    index_url1 = "http://www.infoarena.ro/runda/teme_acmunibuc_2014_1/clasament?rankings_display_entries=50&rankings_first_entry=0"
    index_url2 = "http://www.infoarena.ro/runda/teme_acmunibuc_2014_1/clasament?rankings_display_entries=50&rankings_first_entry=50"
    #30 - 59 5
    #>60 10p

    #pe fiecare grupa de problema 2/3 din probleme
    #media tutoror mai putin cel mai putin scor

    problems = [
        ('par', 'secv6', 'trompeta'),
        ('tsunami', 'cifre4', 'queue'),
        ('qtri', 'grarb', 'tamplar', 'berarii2'),
        ('beri', 'taste', 'grid'),
        ('criptare2', 'mere', 'tdeque', 'noname2'),
        ('patrate6', 'algebra2', 'something'),
        ('patrate3', 'loto', 'pariuri', 'secv5', 'arbore3'),
        ('binar', 'alpin', 'pavare'),
        ('timbre', 'lupu')
    ]

    score_set = []
    user_set = []
    def __init__(self, session=None):
        self.session = session or requests.Session()

    use_cdep_opener = False
    def opener(self, url):
        # we need to pass in all the hooks because of a bug in requests 2.0.0
        # https://github.com/kennethreitz/requests/issues/1655
        resp = self.session.get(url, hooks=self.session.hooks)
        if self.use_cdep_opener:
            text = resp.content.decode('iso-8859-2')
            # we use utf-16 because the parser's autodetect works fine with it
            return text.encode('utf-16')
        else:
            return resp.text

    def fetch_url(self, url, args=None):
        if args:
            if '?' not in url:
                url += '?'
            elif url[-1] not in ['?', '&']:
                url += '&'
            url += urlencode(args)
        logger.debug("Fetching URL %s", url)
        page = pq(url, parser='html', opener=self.opener)
        page.make_links_absolute()
        return page


    def fetch_users(self, index_url):
        #url_set = self.fetch_urls(self.index_url)
        page = self.fetch_url(index_url)
        users = page('table.sortable .normal-user .username a')
        scores = page('table.sortable').find('.number.score')

        for i in range(len(users)):
            self.user_set.append(users.eq(i).text())
        for i in range(len(scores)):
            if i == 0:
                continue
            self.score_set.append(scores.eq(i).text())

    def getscore(self, problems, user):
        user_page = self.fetch_url('http://www.infoarena.ro/runda/teme_acmunibuc_2014_1?user='+user)
        results = []
        for problem in problems:
            v = user_page('table.sortable .task a')
            v = list(
                    filter(
                    lambda element:
                    pq(element).attr('href').split('/')[-1] == problem, v)
                )
            #print (problem, user)
            v =  pq(v[0]).parent().parent().parent().children().eq(3).text()
            #print (problem, v)
            if v == 'N/A':
                results.append(0)
            else:
                results.append(int(v))
        return results

    def go_scrape(self):
        self.fetch_users(self.index_url1)
        self.fetch_users(self.index_url2)
        user_set = self.user_set

        total_problems = self.problems;
        #from pdb import set_trace; set_trace()
        f = open("archive.csv", "w")

        for user_index in range(len(user_set)):
            """
            if (user_index % 5 == 0):
                from time import sleep
                sleep(20)
            """
            user = user_set[user_index]

            v = []
            for problem_group in total_problems:
                points = 0
                scores = zip(problem_group, self.getscore(problem_group, user))

                for problem in scores:
                    temp_score = problem[1]
                    if temp_score >= 30 and temp_score < 60:
                        points += 5
                    if temp_score > 60:
                        points += 10
                L = len(problem_group)

                grade = points / (2.0 * L * 10 / 3.0)
                grade *= 10
                v.append(min([11,grade]))

            v.sort()
            total_score = 0
            for i in range(1, len(v)):
                total_score += v[i]
            total_score /= (len(v) - 1)
            print (user +"," + str(total_score))
        """
        import json
        f = open("dump-result.json", "w")
        json.dump( D, f)
        """

def main():
    infoarena_scraper = Infoarena()
    infoarena_scraper.go_scrape()

if __name__ == "__main__":
    main()
