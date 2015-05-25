'''plugin.py

'''
import ckan
import pylons
import logging
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from pylons import session
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))
import odm_theme_helper
import datetime
import time
from urlparse import urlparse
import json
import collections

log = logging.getLogger(__name__)

def last_dataset():
  '''Returns the last created dataset'''
  return session['last_dataset']

def localize_resource_url(url):
  '''Converts a absolute URL in a relative, chopping out the domain'''

  parsed = urlparse(url)
  str_index = url.index(parsed.netloc)
  str_length = len(parsed.netloc)

  localized = url[str_index+str_length:]

  return localized

def get_tag_dictionaries(vocab_id):
  '''Returns the tag dictionary for the specified vocab_id'''

  try:

    tag_dictionaries = toolkit.get_action('tag_list')(data_dict={'vocabulary_id': vocab_id})
    return tag_dictionaries

  except toolkit.ObjectNotFound:

    return []

def get_tag_dictionaries_json(vocab_id):
  '''Returns the tag dictionary for the specified vocab_id, in json format and adding indexes'''

  return jsonify_list(get_tag_dictionaries(vocab_id))

def jsonify_list(input_list):
  '''Returns the tag dictionary for the specified vocab_id, in json format and adding indexes'''

  log.debug('jsonify_list: %s', input_list)

  items = []

  if not isinstance(input_list, list):
    return items

  for item in input_list:
    items.append({'id':item,'text':get_localized_tag(item)})

  return json.dumps(items)

def jsonify_countries():
  '''Returns the tag dictionary for the countries'''

  log.debug('jsonify_countries')

  items = []
  for country in countries():
    items.append({'id':country[0],'text':country[0]})

  return json.dumps(items)

def jsonify_languages():
  '''Returns the tag dictionary for the languages'''

  log.debug('jsonify_languages')

  items = []
  for language in languages():
    items.append({'id':language[0],'text':language[1]})

  return json.dumps(items)

def validate_not_empty(value,context):
  '''Returns if a string is empty or not'''

  log.debug('validate_not_empty: %s', value)

  if not value or len(value) is None:
    raise toolkit.Invalid('Missing value')
  return value

def get_localized_tag(tag):
  '''Looks for a term translation for the specified tag. Returns the tag untranslated if no term found'''

  log.debug('odm_theme_get_localized_tag: %s', tag)

  desired_lang_code = pylons.request.environ['CKAN_LANG']

  translations = ckan.logic.action.get.term_translation_show(
          {'model': ckan.model},
          {'terms': (tag)})

  # Transform the translations into a more convenient structure.
  for translation in translations:
    if translation['lang_code'] == desired_lang_code:
      return translation['term_translation']

  return tag

def get_localized_tag_string(tags_string):
  '''Returns a comma separated string with the translation of the tags specified. Calls get_localized_tag'''

  log.debug('get_localized_tag_string: %s', tags_string)

  translated_array = []
  for tag in tags_string.split(', '):
    translated_array.append(get_localized_tag(tag))

  if len(translated_array)==0:
    return ''

  return ','.join(translated_array)

def countries():
  '''Return a list of countries'''

  log.debug('countries')

  return odm_theme_helper.countries

def languages():
  '''Return a list of languages'''

  log.debug('languages')

  return odm_theme_helper.languages

def odc_fields():
  '''Return a list of odc fields'''

  log.debug('odc_fields')

  return odm_theme_helper.odc_fields

def metadata_fields():
  '''Return a list of metadata fields'''

  log.debug('metadata_fields')

  return odm_theme_helper.metadata_fields

def popular_groups():
  '''Return a sorted list of the groups with the most datasets.'''

  # Get a list of all the site's groups from CKAN, sorted by number of
  # datasets.
  groups = toolkit.get_action('group_list')(
      data_dict={'sort': 'packages desc', 'all_fields': True})

  # Truncate the list to the 10 most popular groups only.
  groups = groups[:10]

  return groups

def recent_datasets():
  '''Return a sorted list of the datasets updated recently.'''

  # Get a list of all the site's groups from CKAN, sorted by number of
  # datasets.
  dataset = toolkit.get_action('current_package_list_with_resources')(
      data_dict={'limit': 10})

  return dataset

def popular_datasets(limit):
  '''Return a sorted list of the most popular datasets.'''

  # Get a list of all the site's groups from CKAN, sorted by number of
  # datasets.
  result_dict = toolkit.get_action('package_search')(
      data_dict={'sort': 'views_recent desc', 'rows': limit})

  return result_dict['results']

def get_orga_or_group(orga_id,group_id):
  '''Returns orga or group'''

  if orga_id is not None:
    return orga_id
  elif group_id is not None:
    return group_id

  return None

def is_user_admin_of_organisation(organization_name):
  '''Returns wether the current user has the Admin role in the specified organisation'''

  user_id = toolkit.c.userobj.id

  log.debug('is_user_admin_of_organisation: %s %s', user_id, organization_name)

  if organization_name is 'None':
    return False

  try:
    members = toolkit.get_action('member_list')(
    data_dict={'id': organization_name, 'object_type': 'user', 'capacity': 'admin'})

  except toolkit.ObjectNotFound:
    return False

  member_ids = [member_tuple[0] for member_tuple in members]

  try:
    if user_id in member_ids:
      return True

  except toolkit.Invalid:
    return False

  return False

class OdmThemePlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
  '''OD Mekong theme plugin.'''

  plugins.implements(plugins.IDatasetForm)
  plugins.implements(plugins.IConfigurer)
  plugins.implements(plugins.ITemplateHelpers)
  plugins.implements(plugins.IRoutes, inherit=True)
  plugins.implements(plugins.IFacets)
  plugins.implements(plugins.IPackageController, inherit=True)

  def dataset_facets(self, facets_dict, package_type):

      facets_dict = {
                'license_id': toolkit._('License'),
                'organization': toolkit._('Organizations'),
                'groups': toolkit._('Groups'),
                'tags': toolkit._('Tags'),
                'res_format': toolkit._('Formats'),
                'odm_language': toolkit._('Language'),
                'odm_spatial_range': toolkit._('Country')
                }

      return facets_dict

  def group_facets(self, facets_dict, group_type, package_type):

      group_facets = {
                'license_id': toolkit._('License'),
                'organization': toolkit._('Organizations'),
                'tags': toolkit._('Tags'),
                'res_format': toolkit._('Formats'),
                'odm_language': toolkit._('Language'),
                'odm_spatial_range': toolkit._('Country')
                }

      return group_facets

  def organization_facets(self, facets_dict, organization_type, package_type):

      organization_facets = {
                'license_id': toolkit._('License'),
                'groups': toolkit._('Groups'),
                'tags': toolkit._('Tags'),
                'res_format': toolkit._('Formats'),
                'odm_language': toolkit._('Language'),
                'odm_spatial_range': toolkit._('Country')
                }

      return organization_facets

  def before_map(self, m):
    return m

  def update_config(self, config):
    '''Update plugin config'''

    toolkit.add_template_directory(config, 'templates')
    toolkit.add_resource('fanstatic', 'odm_theme')
    toolkit.add_public_directory(config, 'public')

  def get_helpers(self):
    '''Register the plugin's functions above as a template helper function.'''

    return {
      'odm_theme_last_dataset': last_dataset,
      'odm_theme_localize_resource_url': localize_resource_url,
      'odm_theme_get_localized_tag_string': get_localized_tag_string,
      'odm_theme_get_localized_tag': get_localized_tag,
      'odm_theme_popular_groups': popular_groups,
      'odm_theme_recent_datasets': recent_datasets,
      'odm_theme_popular_datasets': popular_datasets,
      'odm_theme_languages': languages,
      'odm_theme_countries': countries,
      'odm_theme_odc_fields': odc_fields,
      'odm_theme_metadata_fields': metadata_fields,
      'odm_theme_get_orga_or_group': get_orga_or_group,
      'odm_theme_is_user_admin_of_organisation': is_user_admin_of_organisation,
      'odm_theme_tag_dictionaries': get_tag_dictionaries,
      'odm_theme_jsonify_list': jsonify_list,
      'odm_theme_jsonify_countries': jsonify_countries,
      'odm_theme_jsonify_languages': jsonify_languages
    }

  def _modify_package_schema_write(self, schema):

    for metadata_field in odm_theme_helper.metadata_fields:
      validators_and_converters = [toolkit.get_validator('ignore_missing'),toolkit.get_converter('convert_to_extras'), ]
      if metadata_field[2]:
        validators_and_converters.insert(1,validate_not_empty)
      schema.update({metadata_field[0]: validators_and_converters})

    for odc_field in odm_theme_helper.odc_fields:
      validators_and_converters = [toolkit.get_validator('ignore_missing'),toolkit.get_converter('convert_to_extras'), ]
      if odc_field[2]:
        validators_and_converters.insert(1,validate_not_empty)
      schema.update({odc_field[0]: validators_and_converters})

    for tag_dictionary in odm_theme_helper.tag_dictionaries:
      schema.update({tag_dictionary[0]: [toolkit.get_validator('ignore_missing'),toolkit.get_converter('convert_to_tags')(tag_dictionary[0])]})

    return schema

  def _modify_package_schema_read(self, schema):

    for metadata_field in odm_theme_helper.metadata_fields:
      validators_and_converters = [toolkit.get_converter('convert_from_extras'),toolkit.get_validator('ignore_missing')]
      if metadata_field[2]:
        validators_and_converters.append(validate_not_empty)
      schema.update({metadata_field[0]: validators_and_converters})

    for odc_field in odm_theme_helper.odc_fields:
      validators_and_converters = [toolkit.get_converter('convert_from_extras'),toolkit.get_validator('ignore_missing')]
      if odc_field[2]:
        validators_and_converters.append(validate_not_empty)
      schema.update({odc_field[0]: validators_and_converters})

    for tag_dictionary in odm_theme_helper.tag_dictionaries:
      schema.update({tag_dictionary[0]: [toolkit.get_converter('convert_from_tags')(tag_dictionary[0]),toolkit.get_validator('ignore_missing')]})

    return schema

  def create_package_schema(self):
    schema = super(OdmThemePlugin, self).create_package_schema()
    schema = self._modify_package_schema_write(schema)
    return schema

  def update_package_schema(self):
    schema = super(OdmThemePlugin, self).update_package_schema()
    schema = self._modify_package_schema_write(schema)
    return schema

  def show_package_schema(self):
    schema = super(OdmThemePlugin, self).show_package_schema()
    schema = self._modify_package_schema_read(schema)
    return schema

  def is_fallback(self):
    return True

  def package_types(self):
    return []

  def before_view(self,pkg_dict):
    log.debug('before_view: %s', pkg_dict)

    session['last_dataset'] = {}

  def after_create(self, context, pkg_dict):
    log.debug('after_create: %s', pkg_dict)

    session['last_dataset'] = pkg_dict

  def after_update(self, context, pkg_dict):
    log.debug('after_update: %s', pkg_dict)
