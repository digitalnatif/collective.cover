# -*- coding: utf-8 -*-

from zope import schema
from zope.interface import implements

from plone.namedfile.field import NamedBlobImage as NamedImage
from plone.namedfile.file import NamedBlobImage as NamedImageFile
from plone.tiles.interfaces import ITileDataManager

from z3c.form.browser.textlines import TextLinesFieldWidget

from plone.autoform import directives as form

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.cover import _
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile


# FIXME: basic tile is not storing the object URL
class IBasicTile(IPersistentCoverTile):

    title = schema.TextLine(
        title=_(u'Title'),
        required=False,
        )

    description = schema.Text(
        title=_(u'Description'),
        required=False,
        )

    image = NamedImage(
        title=_(u'Image'),
        required=False,
        )

    date = schema.Datetime(
        title=_(u'Date'),
        required=False,
        )

    subjects = schema.Tuple(
        title=_(u'label_categories', default=u'Categories'),
        description=_(u'help_categories',
                       default=u'Also known as keywords, tags or labels, these help you categorize your content.'),
        required=False,
        value_type=schema.TextLine(),
        missing_value=(),
        )

    form.widget(tags=TextLinesFieldWidget)


class BasicTile(PersistentCoverTile):

    implements(IPersistentCoverTile)

    index = ViewPageTemplateFile("templates/basic.pt")

    is_configurable = True

    def get_title(self):
        return self.data['title']

    def get_description(self):
        return self.data['description']

    def get_image(self):
        return self.data['image']

    def get_date(self):
        """
        A method to return the date stored in the tile
        """
        if self.data['date'] == None:
            return ''
        formatter = self.request.locale.dates.getFormatter("dateTime", "short")
        datetime_value = self.data['date']
        if datetime_value.year > 1900:
            return formatter.format(datetime_value)
        # due to fantastic datetime.strftime we need this hack
        # for now ctime is default
        return datetime_value.ctime()

    def get_subjects(self):
        """
        A method to return the subjects stored in the tile
        """
        return self.data['subjects']

    def is_empty(self):
        return not(self.data['title'] or \
                   self.data['description'] or \
                   self.data['image'] or \
                   self.data['date'] or \
                   self.data['subjects'])

    def populate_with_object(self, obj):
        super(BasicTile, self).populate_with_object(obj)

        data = {'title': obj.Title(),
                'description': obj.Description()}

        if obj.getField('image'):
            data['image'] = NamedImageFile(obj.getImage().data)

        data_mgr = ITileDataManager(self)
        data_mgr.set(data)

    # XXX: should we accept Collection here?
    def accepted_ct(self):
        """ Return a list of content types accepted by the tile.
        """
        return ['Document', 'File', 'Image', 'Link', 'News Item']
