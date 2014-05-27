import os
import datetime
from unittest import TestCase
from ipernity_api import ipernity, errors
from . import utils


def getfile(fname):
    return os.path.join(os.path.dirname(__file__), 'files', fname)


class IpernityTest(TestCase):
    def __init__(self, *arg, **kwargs):
        TestCase.__init__(self, *arg, **kwargs)
        utils.auto_auth()
        # get a default user
        self.user = utils.AUTH_HANDLER.getUser()
        # fetch some docs for later test
        docs = ipernity.Doc.getList(user=self.user).data
        if not len(docs):  # not docs found, we upload some
            docs = self.upload_files()
        self.docs = docs

    def test_Test(self):
        self.assertEquals('echo', ipernity.Test.echo(echo='echo'))
        self.assertIn('hello', ipernity.Test.hello())

    def test_User(self):
        user_id = self.user.id
        # get user test
        user = ipernity.User.get(id=user_id)
        self.assertIsInstance(user, ipernity.User)
        # filed test
        self.assertIsInstance(user.is_online, bool)
        self.assertIsInstance(user.is_closed, bool)
        self.assertIsInstance(user.is_pro, bool)
        # count test
        self.assertIsInstance(user.count['network'], int)
        self.assertIsInstance(user.dates['member_since'], datetime.datetime)

        # quota test
        quota = user.getQuota()
        self.assertIsInstance(quota.is_pro, bool)
        left = quota.upload['used']['mb']
        self.assertIsInstance(left, int)

    def test_Album(self):
        album = ipernity.Album.create(title='This is a album')
        # fields validation
        self.assertIsInstance(album.count['docs'], int)
        self.assertIsInstance(album.dates['created_at'], datetime.datetime)

        # edit test
        new_title = 'New title'
        new_desc = 'This is a new description'
        album.edit(title=new_title, description=new_desc)
        self.assertEquals(album.title, new_title)
        self.assertEquals(album.description, new_desc)

        album_id = album.id
        # new album can be get
        album = ipernity.Album.get(id=album_id)
        album.delete()
        # after delete, album shoult not found
        with self.assertRaisesRegexp(errors.IpernityAPIError, 'Album not found'):
            ipernity.Album.get(id=album_id)

    def test_Folder(self):
        folder = ipernity.Folder.create(title='folder title')
        # fields type validation
        self.assertIsInstance(folder.count['albums'], int)
        self.assertIsInstance(folder.dates['created_at'], datetime.datetime)

        folder_id = folder.id
        # after created, folder can retrieve by get
        # TODO: this fail
        #folder = ipernity.Folder.get(id=folder_id)

        folder.delete()
        with self.assertRaisesRegexp(errors.IpernityAPIError, 'not found'):
            ipernity.Folder.get(id=folder_id)

    def test_Upload(self):
        ticket = ipernity.Upload.file(file=getfile('1.jpg'))
        ipernity.Upload.checkTickets(tickets=[ticket])
        #ticket.wait_done()
        #doc = ticket.doc
        doc = ticket.getDoc()

        # doc field test
        self.assertIsInstance(doc.dates['created'], datetime.datetime)
        self.assertIsInstance(doc.count['visits'], int)
        self.assertIsInstance(doc.visibility['share'], int)
        self.assertIsInstance(doc.can['fave'], bool)
        self.assertIsInstance(doc.you['visits'], int)
        self.assertIsInstance(doc.owner, ipernity.User)
        doc_str = str(doc)
        self.assertIn('Doc', doc_str)
        self.assertIn('id', doc_str)
        self.assertIn('title', doc_str)

        # thumb test
        thumb = doc.thumbs[0]
        self.assertIsInstance(thumb, ipernity.Thumb)
        self.assertIsInstance(thumb.w, int)
        self.assertIsInstance(thumb.h, int)

        doc.delete()

    def upload_files(self):
        ''' upload some test image and return '''
        def upload_img(fname):
            ticket = ipernity.Upload.file(file=getfile(fname))
            return ticket.getDoc()

        files = ['1.jpg', '2.jpg']
        return [upload_img(fname) for fname in files]
