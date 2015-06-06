# encoding: utf-8

import codecs
import re
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode, getnames
import markdown
from markdown.inlinepatterns import Pattern
import warnings
import os


def warning_on_one_line(message, category, filename, lineno, file=None, line=None):
    return '%s:%s:%s:%s\n' % (category.__name__, filename, lineno,  message)
warnings.formatwarning = warning_on_one_line

# Regular expressions.
CITATION_SIGN = u'@'
MOD_YEAR_ONLY = r'-'
MOD_AUTHOR_ONLY = r'+'
MOD_NOPAREN = r'.'
MOD_NOCITE = r'/'
MODIFIERS = u'[%s%s%s%s]?' % (
    MOD_YEAR_ONLY, MOD_NOCITE, MOD_AUTHOR_ONLY, MOD_NOPAREN)
CITATION_MODIFIERS = u'(?P<mod>%s)' % MODIFIERS
CITATION_KEY = u'[\w_:\*\;\.\-\+\=\/\&\%\$\·\!]+?'
OPTIONAL_PREFIX = u'(\[\s*?(?P<prefix>.*?)\s*?\])?'
OPTIONAL_LOCATOR = u'(\[\s*?(?P<locator>.*?)\s*?\])?'
CITATION_SINGLE = u'@%s%s\(\s*?(?P<key>%s)\s*?\)%s' % (CITATION_MODIFIERS,
                                                       OPTIONAL_PREFIX, CITATION_KEY, OPTIONAL_LOCATOR)
CITATIONS = u'@\((?P<multiple>(\s*?%s(\s*\,\s*%s)+\s*?))\)' % (CITATION_KEY,
                                                               CITATION_KEY)
CITATION = "(%s|%s)" % (CITATION_SINGLE, CITATIONS)


# This dict holds html typesetting instructions for biliography items.
bib_formats = {
    "article": [[u"author_year", u"({})"], [u"author", u", {}"], [u"title", u", <em>{}</em>"],
                [u"journal", u", {}"], [u"volume", u", <strong>{}</strong>"],
                [u"number", u"({})"], [u"pages", u", {}"], [
        u"doi", u""],
        [u"link", u", <code><a href=\"{0}\">{0}</a></code>"]],
    "book": [[u"author_year", u"({})"], [u"author", u", {}"],
             [u"title", u", {}"], [u"volume", ", Volume {}"], [
                 "edition", ", {} Edition"],
             [u"series", ", <i>{}</i>"],  [u"pages", u", {}"],
             [u"doi", u", {}"], [u"url", u", {}"], [u"publisher", ", {}"]],
    "booklet": [[u"author_year", u"({})"],  [u"author", u", {}"],
                [u"title", u", {}"], [u"howpublished", ", {}"], [
                    u"address", ", {}"],
                [u"pages", u", {}"], [u"doi", u", {}"], [u"url", u", {}"]],
    "conference": [[u"author_year", u"({})"], [u"author", u", {}"],
                   [u"title", u", {}"], ["booktitle", ", <i>{}</i>"],
                   [u"editor", ", {} (Ed.)"], [u"organization", ", {}"],
                   [u"publisher", ", {}"], [u"address", ", {}"],
                   [u"pages", u", {}"], [u"doi", u", {}"], [u"url", u", {}"]],
    "inbook": [[u"author_year", u"({})"], [u"author", u", {}"],
               [u"title", u", {}"], ["chapter", ", {}"], [
                   u"editor", ", {} (Ed.)"],
               [u"publisher", ", {}"], [
                   u"address", ", {}"], [u"pages", u", {}"],
               [u"series", ", {}"], [
        u"volume", ", <b>{}</b>"], ["edition", ", {} Edition"],
        [u"doi", u", {}"], [u"url", u", {}"]],
    "incollection": [[u"author_year", u"({})"],  [u"author", u", {}"], [u"booktitle", ", {}"],
                     [u"title", u", {}"], [u"editor", ", {} (Ed.)"],
                     [u"series", ", {}"],  [u"volume", ", <b>{}</b>"],
                     [u"number", ", {}"],  ["edition", ", {} Edition"],
                     [u"organization", ", {}"], [u"publisher", ", {}"],
                     [u"address", ", {}"], [u"pages", u", {}"],
                     [u"doi", u", {}"], [u"url", u", {}"]],
    "misc": [[u"author_year", u"({})"],  [u"author", u", {}"], [u"title", u", {}"],
             [u"howpublished", u", {}"], [u"doi", u", {}"], [u"url", u", {}"],
             [u"year", u", {}"], ],
    "inproceedings": [[u"author_year", u"({})"],  [u"author", u", {}"], [u"title", u", {}"],
                      [u"booktitle", u", {}"], [
                          u"editor", u", {} (Ed)"], [u"pages", u", {}"],
                      [u"organization", u", {}"], [u"publisher", u", {}"],
                      [u"address", u", {}"], [u"doi", u", {}"], [u"url", u", {}"], ],
    "manual": [[u"author_year", u"({})"],  [u"author", u", {}"], [u"title", u", {}"],
               [u"organization", u", {}"], [u"address", u", {}"],
               [u"edition", u", {} Edition"], [u"doi", u", {}"], [u"url", u", {}"], ],
    "phdthesis": [[u"author_year", u"({})"], [u"author", u", {}"],
                  [u"title", u", {} Ph. D."], [
                      u"school", u", {}"], [u"address", u", {}"],
                  [u"doi", u", {}"], [u"url", u", {}"], ],
    "masterthesis": [[u"author_year", u"({})"], [u"author", u", {}"], [u"title", u", {} Ms. D."],
                     [u"school", u", {}"], [
                         u"address", u", {}"], [u"doi", u", {}"],
                     [u"url", u", {}"], ],
    "techreport": [[u"author_year", u"({})"], [u"author", u", {}"],
                   [u"title", u", {}"],  [u"number", u", {}"],
                   [u"institution", u", {}"], [u"address", u", {}"],
                   [u"doi", u", {}"], [u"url", u", {}"], ],
}


def bib_format_record(record):
    s = u""
    for entry in bib_formats.get(record['type'], []):
        value = record.get(entry[0], "")
        if value:
            s += unicode(entry[1]).format(unicode(value))
    s += "."
    return s


class BibtexPattern(markdown.inlinepatterns.Pattern):

    """docstring for BibtexPattern"""

    def __init__(self,  pattern, xtsn):
        markdown.inlinepatterns.Pattern.__init__(self, pattern)
        self.xtsn = xtsn

    def handleMatch(self, m):
        return self.xtsn.handleMatch(m)


class BibtexPostprocessor(markdown.postprocessors.Postprocessor):
    mark = "[REFERENCES]"

    def __init__(self, xtsn):
        markdown.postprocessors.Postprocessor.__init__(self)
        self.xtsn = xtsn

    def run(self, text):
        return text.replace(self.mark, self.xtsn.references())


class BibtexExtension(markdown.extensions.Extension):

    """docstring for BibtexExtension"""

    def __init__(self, *args, **kwargs):
        self.config = {
            'bibliography': ['', 'name of .bib file to load'],
            'root': ['', 'name of the root folder for looking for bibs']
        }
        super(BibtexExtension,self).__init__(*args, **kwargs)
        # if configs:
        #     for key, value in configs:
        #         self.setConfig(key, value)

    def extendMarkdown(self, md, md_globals):
        self.md = md
        # register for reset.
        md.registerExtension(self)
        # insertion in dict before escaping, since key
        # may contain any characters (in principle.)
        md.inlinePatterns.add('bibtex-citation',
                              BibtexPattern(CITATION, self),  "<escape")
        md.postprocessors.add(
            'bibtex-references-list', BibtexPostprocessor(self), "_end")
        # set defaults

        self.reset()

    def reset(self):
        self.author_list = set()
        self.actually_cited = set()
        self.encoding = self.getConfig('encoding', 'utf-8')
        self.records = {}
        self.loaded = False

    def load_bib(self):
        """Load the bibliography. This will be done as late as possible, after a match, in fact."""
        # Take the bibliography from the 'bibliography' key
        # in metadata if there is one, else from the configuration
        if hasattr(self.md, 'Meta') and 'bibliography' in self.md.Meta:
            bibfile = os.path.join(self.getConfig('root'),self.md.Meta['bibliography'][0])
        else:
            bibfile = self.getConfig('bibliography')
        if not bibfile:
            warnings.warn("No bibliography given!")
        else:
            try:
                self.records = self.read_bib(bibfile)
            except:
                warnings.warn(
                    "Some error happened when reading the bibliography")
                self.records = {}
        return True

    def and_authors(self, l):
        if len(l) == 1:
            s = l[0]
        elif len(l) == 2:
            s = l[0] + " and " + l[1]
        elif len(l) == 3:
            s = l[0] + ", " + l[1] + " and " + l[2]
        else:
            s = l[0] + " et al."
        return s

    def digits_base(self, a, b):
        quos = []
        while True:
            quos.append(a % b)
            if a < b:
                break
            a //= b
        return quos[::-1]

    def unique_suffix(self, string):
        s = "abcdefghijklmnopqrstuvxyz"
        i = -1
        suffix = ''
        while string + suffix in self.author_list:
            i += 1
            suffix = "".join([s[t] for t in self.digits_base(i, len(s))])
        self.author_list.add(string + suffix)
        return suffix

    def btex_custom(self, record):
        r = convert_to_unicode(record)
        if "pages" in record:  # fix -- -> –
            if "-" in record["pages"]:
                p = [i.strip().strip('-') for i in record["pages"].split("-")]
                record["pages"] = p[0] + u'–' + p[-1]
        authors = r.get('author')
        if not authors:
            authors = r.get('editor', 'Anon.')
        _authors = getnames(authors.split(" and "))
        _and_surnames = self.and_authors(
            [s.split(",")[0].strip() for s in _authors])
        r['author'] = self.and_authors(_authors)
        r['surnames'] = _and_surnames
        r['author_year'] = _and_surnames + u" " + r['year']
        r['unique_suffix'] = self.unique_suffix(r['author_year'])
        r['author_year'] += r['unique_suffix']
        r['title'] = r['title']  # .replace("{", "").replace("}","")
        return r

    def read_bib(self, bibfile):
        with codecs.open(bibfile, 'r', encoding=self.encoding) as bfil:
            bibtex = bfil.read()
        parsed = BibTexParser(bibtex, customization=self.btex_custom)
        return parsed.get_entry_dict()

    def handleMatch(self, m):
        # This is as late as possible to load data from meta.
        if not self.loaded:
            self.loaded = self.load_bib()

        multiple = m.group('multiple')
        mod = m.group('mod')  # modifiers.
        k, p, l = m.group('key'), m.group('prefix'), m.group('locator')
        field = 'author_year'
        modifier = ''
        paren = True

        def no_extras(p, l, t):
            if p or l:
                warnings.warn(
                    "You can't use prefix or locators in %s" % t.group(2))
            return '', ''

        if multiple:
            p, l = no_extras(p, l, m)
            return self.make_multiple_link(m)

        if mod == MOD_YEAR_ONLY:  # year only
            field = 'year'  # locators are forbidden
            p, l = no_extras(p, l, m)
            modifier = 'year-only'
        elif mod == MOD_AUTHOR_ONLY:  # author only
            field = 'surnames'
            paren = False
            p, l = no_extras(p, l, m)
            modifier = 'author-only'
        elif mod == MOD_NOPAREN:
            paren = False
            # p,l=no_extras(p,l,m)
            modifier = 'no-paren'
        elif mod == MOD_NOCITE:  # nocite
            field = 0
            paren = False
            p, l = no_extras(p, l, m)
            if k == '*':  # \nocite{*}
                self.actually_cited = set(self.records)
            modifier = 'nocite'
        text = self.lookup(k, field) if modifier != "nocite" else ''
        return self.make_link(k, p, l, modifier, text, paren=paren)

    def make_multiple_link(self, m):
        l = [self.make_link(c.strip(), text=self.lookup(
            c.strip(), 'author_year')) for c in m.group('multiple').split(',')]
        e = markdown.util.etree.Element('span', {'class': 'citation-multiple'})
        markdown.util.etree.SubElement(
            e, 'span', {'class': 'citation-open-par'}).text = "("
        e.append(l[0])
        for a in l[1:]:
            markdown.util.etree.SubElement(
                e, 'span', {'class': 'citation-comma'}).text = ", "
            e.append(a)
        markdown.util.etree.SubElement(
            e, 'span', {'class': 'citation-close-par'}).text = ")"
        return e

    def make_link(self, key, prefix='', locator='', modifier='', text='', paren=False):
        d = {
            'data-key': key.strip() if key else '',
            'data-prefix': prefix.strip() if prefix else '',
            'data-locator': locator.strip() if locator else '',
            'data-modifier': modifier.strip() if modifier else'',
            'class': 'citation',
            'href': u'#' + (key.strip() if key else 'xxx')}
        e = markdown.util.etree.Element('a',  d)
        text = text if text else ''
        text = self.compose(text.strip(), d['data-prefix'], d['data-locator'])
        if paren:
            text = u'(' + text + u')'
        e.text = text
        return e

    def lookup(self, k, f):
        fail = '<b>??</b>'
        if k in self.records:
            self.actually_cited.add(k)
            return self.records[k].get(f, '')
        else:
            warnings.warn('Citation "%s" undefined.' % k)
            return fail

    def compose(self, au, p, l):
        s = au
        if p:
            s = p + " " + au
        if l:
            s += ", " + l
        return s

    def references(self):
        ul = [self.records[k] for k in self.actually_cited]
        ul.sort(key=lambda x: x['author_year'])
        return ('\n<ul class="citation-references">\n'
                + "\n".join(['<li class="citation-item" id="%s">%s</li>' % (r['id'], bib_format_record(r))
                             for r in ul])
                + "\n</ul>\n")


def makeExtension(*args, **kwargs):
    #return BibtexExtension(configs=configs)
    return BibtexExtension(*args, **kwargs)

# @(key)    non greedy, allow escaped.
# @[suffix](key)
# @(key)[locator]
# @[prefix](key)[locator]
# @/(key)   nocite key
# @/(*)     nocite all
# @-(key)     only year
# @+(key)     only name
# @(key,key,key,...)

# if __name__ == "__main__":
#
#     text=u"""Bibliography: example.bib
#
# In file `example.bib`
#
#     @article{aamport86,
#       Author = {Leslie A. Aamport},
#       Journal = {G-Animal's Journal},
#       Month = jul,
#       Number = 7,
#       Pages = {73+},
#       Title = {The Gnats and Gnus Document Preparation System},
#       Volume = 41,
#       Year = 1986}
#
#     @inbook{knuth73,
#       Address = {Reading, Massachusetts},
#       Author = {Donald E. Knuth},
#       Chapter = {1.2},
#       Edition = {Second},
# Month = {10 } # jan,
#       Pages = {10--119},
#       Publisher = {Addison-Wesley},
#       Series = {The Art of Computer Programming},
#       Title = {Fundamental Algorithms},
#       Type = {Section},
#       Volume = 1,
#       Year = {1973}}
#
#     @techreport{vanRossum95,
#       Address = {Amsterdam},
#       Author = {Guido van Rossum},
#       Institution = {Centrum voor Wiskunde en Informatica (CWI)},
#       Number = {Technical Report CS-R9526},
#       Title = {Python tutorial},
#       Year = {1995}}
#
#
#
# 1. Simplest of all: `@(knuth73)` produces @(knuth73).
# 4. You can use a prefix or a locator, or both; and also there's some whitespace allowed: `@[ see ]( aamport86 )[ chapter 11 ]` produces @[ see ]( aamport86 )[ chapter 11 ].
# 5. Just the year `@-(knuth73)` gives @-(knuth73).
# 6. Just the author: `@+(knuth73)[ch. 3]` gives @+(knuth73)[ch. 3], and a warning, since the correct form is `@+(knuth73)`. You can use these last two together: @+(knuth73) says @-(knuth73) that ...
# 2. `@.(knuth73)` writes the citation with no parenthesis.
# 7. A nocite command (no output): `@/(knuth73)` or  `@/(*)`.@/(*)
# 8. Compound citation @(aamport86, knuth73)
#
# References
#
# [REFERENCES]
#
#     """
#
#     m=markdown.Markdown(extensions=['bib', 'meta'])
#
#     print m.convert(text).encode('utf-8')
#
#
