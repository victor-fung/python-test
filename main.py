import os
import random

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

DEFAULT_GHOSTNAME_LIST = 'default'

# Set a parent key on the 'GhostNames' to ensure that they are all
# in the same entity group. This allows us to extend our application
# if we are introducing multiple groups of ghost names
# Set parent key to 'default' for now

def ghostnamelist_key(ghostname_list=DEFAULT_GHOSTNAME_LIST):
    """Constructs a Datastore key for a GhostNameList entity.

    We use ghostname_list as the key.
    """
    return ndb.Key('GhostNameList', ghostname_list)

# Function for checking if user is admin
def user_is_admin():
  user = users.get_current_user()
  if user:
      if users.is_current_user_admin():
          return True
      else:
          return False
  else:
      return False

class GhostNameTaker(ndb.Model):
    """Sub model for representing an ghostname taker."""
    identity = ndb.StringProperty(indexed=True, required=True)
    email = ndb.StringProperty(indexed=False, required=True)
    first_name = ndb.StringProperty(indexed=False, required=True)
    last_name = ndb.StringProperty(indexed=False, required=True)


class GhostName(ndb.Model):
    """A main model for representing an individual GhostNameList entry."""
    ghost_name = ndb.StringProperty(indexed=False, required=True)
    taker = ndb.StructuredProperty(GhostNameTaker)
    is_taken = ndb.BooleanProperty(default=False)
    date_created = ndb.DateTimeProperty(auto_now_add=True)
    date_modified = ndb.DateTimeProperty(auto_now=True)

class OverviewPage(webapp2.RequestHandler):
    def get(self):

        is_admin = False

        if user_is_admin():
            is_admin = True

        logout_url = ''
        logout_url_linktext = ''

        ghostname_query = GhostName.query(
            ancestor=ghostnamelist_key()).order(-GhostName.date_modified)
        ghostnames = ghostname_query.fetch()

        user = users.get_current_user()

        if user:
            current_ghostname_query = GhostName.query(
                ancestor=ghostnamelist_key()).filter(GhostName.taker.identity==users.get_current_user().user_id(),GhostName.is_taken==True)
            current_ghostname = current_ghostname_query.get()
            if current_ghostname:
                url = '/pick_ghostname'
                url_linktext = 'Change your current Phantom name'
            else:
                url = '/pick_ghostname'
                url_linktext = 'Get a Phantom name'

            logout_url = users.create_logout_url(self.request.uri)
            logout_url_linktext = 'Logout'
        else:
            url = users.create_login_url('/pick_ghostname')
            url_linktext = 'Get a Phantom name'

        template_values = {
            'user': user,
            'button_text': url_linktext,
            'button_url': url,
            'logout_button_text': logout_url_linktext,
            'logout_button_url': logout_url,
            'ghostnames': ghostnames,
            'is_admin': is_admin,
            'admin_button_text': 'Add Ghost Name',
            'admin_button_url': '/add_ghost_name'
        }

        template = JINJA_ENVIRONMENT.get_template('overview.html')
        self.response.write(template.render(template_values))

class PickGhostNameFormPage(webapp2.RequestHandler):
    def post(self):
      is_admin = False
      error_message = False
      validation_passed = True

      if user_is_admin():
          is_admin = True

      user = users.get_current_user()
      if user:
          first_name = self.request.get('first_name').strip()
          last_name = self.request.get('last_name').strip()
          chosen_ghost_name = self.request.get('ghost_name').strip()

          current_ghostname_query = GhostName.query(
              ancestor=ghostnamelist_key()).filter(GhostName.taker.identity==users.get_current_user().user_id(),GhostName.is_taken==True)

          current_ghostname = current_ghostname_query.get()

          if not (len(first_name)>0 and len(last_name)>0 and len(chosen_ghost_name)>0):
              validation_passed = False
              error_message = 'All fields are required, please try again'

          if validation_passed:
              ghostname_update = GhostName.get_by_id(int(chosen_ghost_name),parent=ghostnamelist_key())

              current_ghostname_query = GhostName.query(
                  ancestor=ghostnamelist_key()).filter(GhostName.taker.identity==users.get_current_user().user_id(),GhostName.is_taken==True)
              current_ghostname = current_ghostname_query.get()

              if ghostname_update:
                  if (not ghostname_update.is_taken) or (current_ghostname and current_ghostname.key.id()==int(chosen_ghost_name)):
                      ghostname_update.taker = GhostNameTaker(
                              identity = users.get_current_user().user_id(),
                              email = users.get_current_user().email(),
                              first_name = first_name,
                              last_name = last_name
                      )
                      ghostname_update.is_taken = True
                      updated_key = ghostname_update.put()
                      if current_ghostname and current_ghostname.key.id()!=int(chosen_ghost_name):
                          current_ghostname.is_taken = False
                          current_ghostname.taker = None
                          current_ghostname.put()
                      self.redirect('/')
                  else:
                      error_message = 'Sorry, this ghost name has just got taken, please try again'
              else:
                  error_message = 'Sorry, ghost name does not exist, please try again'


          ghostname_query = GhostName.query(
              ancestor=ghostnamelist_key()).filter(GhostName.is_taken==False)

          ghostnames = ghostname_query.fetch()

          random.shuffle(ghostnames)

          randomThreeGhostNames = []

          for ghostname in ghostnames:
              if len(randomThreeGhostNames) < 3:
                randomThreeGhostNames.append(ghostname)
              else:
                  break

          if len(randomThreeGhostNames) == 0:
              error_message = 'Sorry! All ghost names are taken'

          template_values = {
              'is_admin': is_admin,
              'admin_button_text': 'Add Ghost Name',
              'admin_button_url': '/add_ghost_name',
              'button_text': 'Logout',
              'button_url': users.create_logout_url('/'),
              'overview_button_text': 'Overview',
              'overview_button_url': '/',
              'error_message': error_message,
              'ghostnames': randomThreeGhostNames,
              'current_ghostname': current_ghostname,
              'first_name': first_name,
              'last_name': last_name

          }
      else:
          template_values = {
            'overview_button_text': 'Overview',
            'overview_button_url': '/',
            'button_text': 'Get a Phantom name',
            'button_url': users.create_login_url(self.request.uri),
            'error_message': 'Access Denied, please click on "Get a Phantom name" button on the top right to get a phantom name'
          }

      template = JINJA_ENVIRONMENT.get_template('pick_ghost_name.html')
      self.response.write(template.render(template_values))
    def get(self):
        is_admin = False

        if user_is_admin():
            is_admin = True

        user = users.get_current_user()
        if user:
            first_name = ''
            last_name = ''

            current_ghostname_query = GhostName.query(
                ancestor=ghostnamelist_key()).filter(GhostName.taker.identity==users.get_current_user().user_id(),GhostName.is_taken==True)

            current_ghostname = current_ghostname_query.get()

            if current_ghostname:
                first_name = current_ghostname.taker.first_name
                last_name = current_ghostname.taker.last_name

            ghostname_query = GhostName.query(
                ancestor=ghostnamelist_key()).filter(GhostName.is_taken==False)

            ghostnames = ghostname_query.fetch()

            random.shuffle(ghostnames)

            randomThreeGhostNames = []

            for ghostname in ghostnames:
                if len(randomThreeGhostNames) < 3:
                  randomThreeGhostNames.append(ghostname)
                else:
                    break

            error_message = False

            if len(randomThreeGhostNames) == 0:
                error_message = 'Sorry! All ghost names are taken'

            template_values = {
                'overview_button_text': 'Overview',
                'overview_button_url': '/',
                'is_admin': is_admin,
                'admin_button_text': 'Add Ghost Name',
                'admin_button_url': '/add_ghost_name',
                'button_text': 'Logout',
                'button_url': users.create_logout_url('/'),
                'error_message': error_message,
                'ghostnames': randomThreeGhostNames,
                'current_ghostname': current_ghostname,
                'first_name': first_name,
                'last_name': last_name
            }
        else:
            template_values = {
              'overview_button_text': 'Overview',
              'overview_button_url': '/',
              'button_text': 'Get a Phantom name',
              'button_url': users.create_login_url(self.request.uri),
              'error_message': 'Please click on "Get a Phantom name" button on the top right to get a phantom name'
            }

        template = JINJA_ENVIRONMENT.get_template('pick_ghost_name.html')
        self.response.write(template.render(template_values))

class AddGhostNameFormPage(webapp2.RequestHandler):
    def get(self):
        if user_is_admin():
            template_values = {
              'button_text': 'Logout',
              'button_url': users.create_logout_url('/'),
            }
            template = JINJA_ENVIRONMENT.get_template('add_ghost_name.html')
            self.response.write(template.render(template_values))
        else:
            self.response.write('Access Denied')
    def post(self):

        if user_is_admin():
            success = False

            for i in range(1,21):
              name = self.request.get('ghost_name_'+`i`)
              if name:
                ghostname = GhostName(parent=ghostnamelist_key())
                ghostname.ghost_name = name
                new_ghost_name = ghostname.put()
                success = True
              else:
                  break

            if success:
              template_values = {
                  'success_message': 'New ghost name(s) succesfully added',
                  'button_text': 'Logout',
                  'button_url': users.create_logout_url('/')
              }
            else:
               template_values = {
                   'error_message': 'New ghost name failed to add, please try again',
                   'button_text': 'Logout',
                   'button_url': users.create_logout_url('/')
               }
            template = JINJA_ENVIRONMENT.get_template('add_ghost_name.html')
            self.response.write(template.render(template_values))
        else:
            self.response.write('Access Denied')


app = webapp2.WSGIApplication([
    ('/', OverviewPage),
    ('/add_ghost_name',AddGhostNameFormPage),
    ('/pick_ghostname',PickGhostNameFormPage)
], debug=True)
