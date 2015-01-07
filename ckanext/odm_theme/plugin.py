'''plugin.py

'''
import logging
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))
import odm_theme_helper

log = logging.getLogger(__name__)

def metadata_fields():
    '''Return a list of metadata fields'''

    log.debug('metadata_fields')

    return odm_theme_helper.metadata_fields

def most_popular_groups():
    '''Return a sorted list of the groups with the most datasets.'''

    # Get a list of all the site's groups from CKAN, sorted by number of
    # datasets.
    groups = toolkit.get_action('group_list')(
        data_dict={'sort': 'packages desc', 'all_fields': True})

    # Truncate the list to the 10 most popular groups only.
    groups = groups[:10]

    return groups

def is_user_admin_of_organisation(organization_name):

    '''Returns wether the current user has the Admin role in the specified organisation'''

    user_id = toolkit.c.userobj.id

    log.debug('is_user_admin_of_organisation: %s %s', user_id, organization_name)

    if organization_name is 'None':

        return False

    try:

        # Retrieve admin members from the specified organisation
        members = toolkit.get_action('member_list')(
        data_dict={'id': organization_name, 'object_type': 'user', 'capacity': 'admin'})

    except toolkit.ObjectNotFound:

        return False

    # 'members' is a list of (user_id, object_type, capacity) tuples, we're
    # only interested in the user_ids.
    member_ids = [member_tuple[0] for member_tuple in members]

    try:

        # Finally, we can test whether the user is a member of the curators group.
        if user_id in member_ids:

            return True

    except toolkit.Invalid:

        return False

    return False

class OdmThemePlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    '''ODM theme plugin.

    '''

    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)

    def update_config(self, config):

        toolkit.add_template_directory(config, 'templates')
        toolkit.add_resource('fanstatic', 'odm_theme')

    def get_helpers(self):
        '''Register the plugin's functions above as a template helper function.

        '''
        return {
            'odm_theme_most_popular_groups': most_popular_groups,
            'odm_theme_metadata_fields': metadata_fields,
            'odm_theme_is_user_admin_of_organisation': is_user_admin_of_organisation
        }

    def _modify_package_schema_write(self, schema):

        for field in odm_theme_helper.metadata_fields:
          schema.update({
              field[0]: [toolkit.get_validator('ignore_missing'),toolkit.get_converter('convert_to_extras')]
          })

        for taxonomy in odm_theme_helper.taxonomy_fields:
          schema.update({
              taxonomy[0]: [toolkit.get_validator('ignore_missing'),toolkit.get_converter('convert_to_tags')(taxonomy[0])]
          })

        return schema

    def _modify_package_schema_read(self, schema):

        for field in odm_theme_helper.metadata_fields:
          schema.update({
              field[0]: [toolkit.get_converter('convert_from_extras'),toolkit.get_validator('ignore_missing')]
          })

        for taxonomy in odm_theme_helper.taxonomy_fields:
          schema.update({
              taxonomy[0]: [toolkit.get_converter('convert_from_tags')(taxonomy[0]),toolkit.get_validator('ignore_missing')]
          })

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
