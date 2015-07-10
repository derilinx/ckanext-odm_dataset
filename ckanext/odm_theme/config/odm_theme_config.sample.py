# -*- coding: utf-8 -*-
''' Module containing config variables for scripts, please rename to odm_theme_config.py

'''

#DEBUG
DEBUG = False

#Control logic
SKIP_N_DATASETS = 0
SKIP_EXISTING = False

#Common
CKAN_URL='URL'
CKAN_APIKEY='KEY'

# Geoserver
GEOSERVER_URL='URL'
GEOSERVER_AUTH='AUTH'
GEOSERVER_MAP={'ontology':'*','organization':'cambodia-organization','groups':[{'name':'maps-group'}],'package_type':'dataset'}

# NewGenLib
NGL_URL='URL'
NGL_MAP={'ontology':'*','organization':'odm-library','groups':[],'package_type':'library_record'}

# ODC
ODC_MAP=[{'ontology':'ODC/laws','organization':'cambodia-organization','groups':[{'name':'laws-group'}],'field_prefixes':[{'field':'file_name_kh','prefix':'https://cambodia.opendevelopmentmekong.net/wp-content/blogs.dir/2/download/law/'},{'field':'file_name_en','prefix':'https://cambodia.opendevelopmentmekong.net/wp-content/blogs.dir/2/download/law/'}],'package_type':'dataset'}]

# Insert initial data
ODM_ADMINS_PASS='odmadmin'

# Delete datasets in group
DELETE_MAP={'organization':'odm-library','group':'laws-group','state':'draft','limit':500,'field_filter':{'odm_contact':'OD Mekong Importer','odm_contact_email':'info@opendevmekong.net'}}

# Change type of datasets in group
CHANGE_TYPE_MAP={'type':'library_record','organization':'odm-library','state':'active','limit':500,'field_filter':{'odm_contact':'OD Mekong Importer','odm_contact_email':'info@opendevmekong.net'}}

# Tag vocabularies
TAXONOMY_TAG_VOCAB='taxonomy'
SUPPORTED_LANGS=['en','vi','th', 'km']

# Importer infos
IMPORTER_NAME='OD Mekong Importer'
IMPORTER_EMAIL='info@opendevmekong.net'
