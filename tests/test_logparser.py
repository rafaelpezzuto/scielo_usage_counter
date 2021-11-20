import unittest
import datetime

from app.utils.logparser import LogParser


class TestLogParser(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.lp = LogParser('data/map.mmdb', 'data/counter-robots.txt')

    def test_action_is_static_file_true(self):
        static_urls = [
            '/img/revistas/rbp/v26n3/a13img02.gif',
            '/img/revistas/pab/v47n8/a19tab02.jpg',
            '/img/revistas/cr/v47n7//1678-4596-cr-47-07-e20161076-gt2.svg',
            '/applications/scielo-org/js/toolbox.js',
            '/applications/scielo-org/css/public/style-es.css',
            '/applications/scielo-org/js/jquery-1.4.2.min.js',
            '/img/revistas/rbgo/v34n1/a07tab02.jpg',
        ]

        for url in static_urls:
            obtained = self.lp.action_is_static_file(url)
            self.assertTrue(obtained)

    def test_action_static_file_false(self):
        not_static_urls = [
            '/scielo.php?script=sci_arttext&pid=S1806-37132013000500595',
            '/scielo.php?script=sci_arttext&pid=S0101-20612008000500011&lng=en&nrm=iso&tlng=pt',
            '/pdf/rbfis/v12n5/en_a09v12n5.pdf',
            '/google_metrics/get_h5_m5.php?issn=1413-6538&callback=jsonp1530327621274',
            '/scielo.php?script=sci_serial&pid=1678-6971&lng=en&nrm=iso',
            '/favicon.ico?script=sci_arttext&pid=S0102-35862003000500003',
            '/cgi-bin/wxis.exe/iah/?IsisScript=iah/iah.xis&base=title&fmt=iso.pft&lang=p',
        ]

        for url in not_static_urls:
            obtained = self.lp.action_is_static_file(url)
            self.assertFalse(obtained)

    def test_action_download_true(self):
        download_urls = [
            '/pdf/abo/v64n3/12518.pdf',
            '/img/revistas/bn/v18n2/1676-0611-bn-1676-0611-BN-2017-0395-suppl3-m01.mp4',
            '/pdf/anp/v71n9B/0004-282X-anp-71-09b-693.pdf',
            '/pdf/rbof/v66n6/a02v66n6.pdf',
            '/pdf/brag/v73n3/pt_aop_brag_0136.pdf',
            '/pdf/bjce/v19n2/10670.pdf',
            '/pdf/%0D/jbpneu/v31n5/27160.pdf',
            '/pdf/ca/v22n5/v22n5a09.pdf',
            '/pdf/fb/v28n5/17673.pdf',
            '/pdf/rbefe/v29n3/1981-4690-rbefe-29-03-00439.pdf',
            '/pdf/rod/v58n4/2175-7860-rod-58-04-0743.pdf',
            '/img/revistas/csc/v22n11/1413-8123-csc-22-11-3537.mp3',
            '/img/revistas/csp/links_ing.doc',
        ]

        for url in download_urls:
            obtained = self.lp.action_is_download(url)
            self.assertTrue(obtained)

    def test_action_download_false(self):
        not_download_urls = [
            '/pdf/rbcpol/n6/n6a04',
            '/favicon.ico?script=sci_arttext&pid=S0102-35862003000500003'
            '/cgi-bin/wxis.exe/iah/?IsisScript=iah/iah.xis&base=title&fmt=iso.pft&lang=p'
        ]

        for url in not_download_urls:
            obtained = self.lp.action_is_download(url)
            self.assertFalse(obtained)

    def test_user_agent_is_bot_true(self):
        ua_bots = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/600.2.5 (KHTML, like Gecko) Version/8.0.2 Safari/600.2.5 (Applebot/0.1; +http://www.apple.com/go/applebot)",
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
        ]

        for ua in ua_bots:
            obtained = self.lp.user_agent_is_bot(ua)
            self.assertTrue(obtained)

    def test_user_agent_is_bot_false(self):
        not_ua_bots = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534+ (KHTML, like Gecko) BingPreview/1.0b",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36",
        ]

        for ua in not_ua_bots:
            obtained = self.lp.user_agent_is_bot(ua)
            self.assertFalse(obtained)

    def test_format_date(self):
        str_date = '4/Nov/2011:00:05:23'
        str_zone = '-0300'
        test_date = datetime.datetime(2011, 11, 4, 3, 5, 23).strftime('%Y-%m-%d %H:%M:%S')
        obtained_date = self.lp.format_date(str_date, str_zone)

        self.assertEqual(test_date, obtained_date)