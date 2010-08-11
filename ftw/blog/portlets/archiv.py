from zope.component import getUtility
from zope.interface import implements
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ftw.blog.interfaces import IBlogUtils
from DateTime import DateTime

MONTHS_GER = {
            '01': u'Januar',
            '02': u'Februar',
            '03': unicode('M\xc3\xa4rz', 'utf-8'),
            '04': u'April',
            '05': u'Mai',
            '06': u'Juni',
            '07': u'Juli',
            '08': u'August',
            '09': u'September',
            '10': u'Oktober',
            '11': u'November',
            '12': u'Dezember',
}


class IArchivePortlet(IPortletDataProvider):
    """
    """


class Assignment(base.Assignment):
    implements(IArchivePortlet)

    @property
    def title(self):
        return "Blog Archive Portlet"

class Renderer(base.Renderer):

    def __init__(self, context, request, view, manager, data):
        self.context = context
        self.data = data
        self.request = request
        self._translation_service = getToolByName(
                                        context,
                                        'translation_service')

    @property
    def available(self):
        """Only show the portlet, when the blog isn't empty
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        blogutils = getUtility(IBlogUtils, name='ftw.blog.utils')
        blogroot = blogutils.getBlogRoot(self.context)
        root_path ='/'.join(blogroot.getPhysicalPath())

        all_entries = catalog({'path': root_path,
                              'portal_type': 'BlogEntry'})
        if len(all_entries) > 0:
            return True
        else:
            return False


    def zLocalizedTime(self, time, long_format=False):
        """Convert time to localized time
        """
        return u"%s %s" % (MONTHS_GER[time.strftime("%m")],
                           time.strftime('%Y'))

    def update(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        blogutils = getUtility(IBlogUtils, name='ftw.blog.utils')
        blogroot = blogutils.getBlogRoot(self.context)
        root_path ='/'.join(blogroot.getPhysicalPath())

        allEntries = catalog({'path': root_path,
                              'portal_type': 'BlogEntry'})

        values = {}
        for entry in allEntries:
            value = entry.created
            key = value.strftime('%B %Y')
            if not key in values:
                values[key] = value
        values = values.values()
        values.sort(reverse=1)

        infos = []
        for v in values:
            # calc the number of items for the month
            start = DateTime(v.strftime('%Y/%m/01'))
            end = DateTime('%s/%s/%s' % (start.year(), start.month()+ 1, start.day()))
            end = end - 1
            number = len(self.context.portal_catalog(portal_type='BlogEntry', path=root_path, created= {'query':(start, end), 'range': 'min:max'}))

            infos.append(dict(
                title = self.zLocalizedTime(v),
                number=number,
                url = blogroot.absolute_url()+ \
                    '/view?archiv=' + \
                    v.strftime('%Y/%m/01')))
                

        self.archivlist = infos

    render = ViewPageTemplateFile('archiv.pt')


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
