import htmllib, formatter
import StringIO
import symantec.machines.utils.html2text as html2text

def text(html):
    return html2text.html2text(html)

def text_def( html ):
    # create memory file
    file = StringIO.StringIO()

    # convert html to text
    f = formatter.AbstractFormatter(formatter.DumbWriter(file))
    p = htmllib.HTMLParser(f)
    p.feed(html)
    p.close()
    """
    if p.anchorlist:
        file.write("\n\nlinks:\n")
        i = 1
        for anchor in p.anchorlist:
            file.write("%d: %s\n" % (i, anchor))
            i = i + 1
    """

    return p.body

