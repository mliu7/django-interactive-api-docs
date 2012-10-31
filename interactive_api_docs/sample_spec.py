"""
This file is used to denote the entire specification for the API. 
"""
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.utils import simplejson

GET_LIMIT_MAX = 20


def clean(method, *args, **kwargs):
    """ A simple decorator to be used on the Params class.
        It cleans up the types by making them more descriptive and also adds any default parameters not specified 
    """
    def wrapped(self, *args, **kwargs):
        params = method(self, *args, **kwargs)
        return self._add_global_defaults(self._clean_types(params))
    return wrapped


class Params(object):
    """ To create the parameters for a resource, subclass this Params class and then define the following methods:

        id_params() - return a dict of all the parameters pertaining to the id of the resource (listed in the URI)
        filter_params() - return a dict of all the parameters that a user can filter a list of this resource on
        update_params() - return a dict of all the parameters a user can update
        create_params() - return a dict of all the parameters a user can input when creating an object

        To then use this class to generate cleaned up dicts of parameter information, call the following methods:

        get_list_params() - returns params for a resource list
        get_detail_params() - returns params for getting a single resource
        get_update_params() - returns params for updating a single resource
        get_create_params() - returns params for creating a single resource
        get_delete_params() - returns params for deleting a single resource


        Each parameter can take the following parameters:
            name - what the parameter is called
            type - the type, such as integer or positive_integer
            required - True or False
            synopsis - Very short description of the parameter (<10 words)
            description - Longer description of the parameter if necessary
            initial - An initial value that the user will see entered in already
            default - If the parameter has a default value, this is used to specify it
            options - A discrete list of options that a user can choose from
            example - A single example
            examples - Multiple comma-separated examples
    """

    type_mappings = [
        {'type': 'integer', 
         'type_detail': 'Integer'},
        {'type': 'positive_integer',
         'type_detail': 'Positive Integer'},
        {'type': 'counting_integer',
         'type_detail': 'Positive integer greater than or equal to 1'},
        {'type': 'decimal',
         'type_detail': 'Decimal',
         'examples': '1, 1.53'},
        {'type': 'string',
         'type_detail': 'String'},
        {'type': 'json',
         'type_detail': 'JSON object'},
        {'type': 'string',
         'type_detail': 'String'},
        {'type': 'integer_list',
         'examples': '[], [1,2,3], [ 23 , 54 ]',
         'type_detail': 'JSON list of comma separated positive integers'},
        {'type': 'string_list',
         'examples': '[], [param_1, param_2]',
         'type_detail': 'List of comma separated strings'},
        {'type': 'iso_format',
         'type_detail': 'ISO 8601 format time string. Form is YYYY-MM-DDTHH:MM:SS&#177;hh:mm',
         'example': '2012-01-23T13:15:00-06:00 represents 1:15pm Jan 23rd 2012, Central Standard Time'},
        {'type': 'date',
         'type_detail': 'Date string. Form is YYYY-MM-DD',
         'example': '2012-01-23 represents Jan 23rd 2012'},
        {'type': 'html',
        {'type': 'boolean',
         'type_detail': 'Boolean. Either True or False'},
        {'type': 'country',
         'type_detail': 'The <a href="http://en.wikipedia.org/wiki/ISO_3166-1" target="_blank">ISO 3166-1</a> Alpha-2 code for the country',
         'example': "'US' is the ISO 3166-1 country code for the United States"},
        
    ]

    @clean
    def get_list_params(self):
        return self.filter_params() + self._global_list_params() + self.paging_params()

    @clean
    def get_detail_params(self):
        return self.id_params() + self._global_detail_params()

    @clean
    def get_update_params(self):
        return self.id_params() + self.update_params() + self._global_update_params()

    @clean
    def get_create_params(self):
        return self.create_params() + self._global_create_params()

    @clean
    def get_delete_params(self):
        return self.id_params() + self._global_delete_params()

    def _add_global_defaults(self, param_dicts):
        """ Adds global default values to the parameter dict.
        
            These global defaults refer to default settings for a single field if they are not explicitly set. 
        """
        global_defaults = {'required': False}
        final_param_dicts = []
        for param_dict in param_dicts:
            for global_default_key in global_defaults.keys():
                if not param_dict.get(global_default_key):
                    # if the param dict doesn't have the key of the global default, add the key/value pair
                    param_dict[global_default_key] = global_defaults[global_default_key]
            final_param_dicts.append(param_dict)
        return final_param_dicts

    def _clean_types(self, param_dicts):
        """ Takes in a parameter dict and replaces types with a more descriptive name. """
        type_mappings = self.type_mappings
        final_param_dicts = []
        for param_dict in param_dicts:
            for type_mapping in type_mappings:
                if param_dict['type'] == type_mapping['type']:
                    # Replace the type with a more detailed type
                    param_dict['type'] = type_mapping['type_detail']

                    # If these parameters are not overridden, add them
                    params_to_add = ['example', 'examples', 'options']
                    for param in params_to_add:
                        param_value = type_mapping.get(param)
                        if param_value and not param_dict.get(param):
                            param_dict[param] = param_value

            final_param_dicts.append(param_dict)
        return final_param_dicts

    def _global_list_params(self):
        """ Returns a list of params that should be added to all list methods by default """
        return [
            {'name': 'order_by',
             'type': 'string_list',
             'exampls': '[id], [-name, -id]',
             'synopsis': ('List of resource attributes you want to order on. Add a minus (-) '
                          'sign in front of the attribute name to order in reverse')},
            {'name': 'fields',
             'exampls': '[id], [id, name]',
             'type': 'string_list',
             'synopsis': ('List of the resource attributes you want returned. If this field is '
                          'left blank, everything will be returned. For resources with a lot of '
                          'nested attributes, this can greatly reduce response time')}
        ]

    def _global_create_params(self):
        """ Returns a list of params that should be added to all create methods by default """
        return []

    def _global_detail_params(self):
        return []

    def _global_update_params(self):
        return []

    def _global_delete_params(self):
        return []

    def paging_params(self):
        faq_url = reverse('user_docs_api_faq')
        return [
            {'name': 'limit',
             'type': ('Positive Integer '
                     '<a target="_blank" href="{0}#limit_and_offset">'
                     'more info</a>'.format(faq_url)),
             'initial': '',
             'default': '20',
             'synopsis': 'The number of objects you want returned.  Maximum ' + str(GET_LIMIT_MAX)},
            {'name': 'offset',
             'type': ('Positive Integer '
                     '<a target="_blank" href="{0}#limit_and_offset">'
                     'more info</a>'.format(faq_url)),
             'initial': '',
             'default': '0',
             'synopsis': 'The index of the first object you want returned in the list'},
        ]

    def update_params(self):
        return self.create_params()


class OrganizationParams(Params):
    def id_params(self):
        return [
            {'name': 'organization_id',
             'type': 'positive_integer',
             'initial': 2,
             'required': True,
             'synopsis': 'ID of the desired organization'}
        ]

    def filter_params(self):
        return [
            {'name': 'organization_ids',
             'type': 'integer_list',
             'synopsis': 'List of IDs of the desired organizations'},
            {'name': 'name',
             'type': 'string',
             'synopsis': "Filter on organizations by their names (case insensitive)"},
            {'name': 'short_name',
             'type': 'string',
             'examples': 'MUFA, USAU, UOA',
             'synopsis': 'Filter on organizations by their abbreviated/shortened name (case insensitive)'}
        ]

    def create_params(self):
        return [
            {'name': 'name',
             'type': 'string',
             'required': True,
             'initial': 'USA Ultimate',
             'examples': 'Madison Ultimate Frisbee Association, USA Ultimate',
             'synopsis': 'Full name of the organization'},
            {'name': 'short_name',
             'type': 'string',
             'required': True,
             'initial': 'USAU',
             'examples': 'MUFA, USAU, UOA',
             'synopsis': 'Abbreviated/shortened name for the organization'}
        ]


class LeagueParams(Params):
    def id_params(self):
        return [
            {'name': 'league_id',
             'type': 'positive_integer',
             'initial': 16,
             'required': True,
             'synopsis': 'ID of the desired league'}
        ]

    def filter_params(self):
        return [
            {'name': 'organization_id',
             'type': 'positive_integer',
             'initial': 2,
             'synopsis': 'Returns leagues within an organization'},
            {'name': 'league_ids',
             'type': 'positive_integer',
             'synopsis': 'Returns leagues matching one or more IDs'},
            {'name': 'sport',
             'type': 'sport',
             'synopsis': 'Returns leagues within a sport'}, 
            {'name': 'gender',
             'type': 'gender',
             'synopsis': 'Returns leagues for a certain gender'},
            {'name': 'name',
             'type': 'string',
             'synopsis': "Filter on leagues by their names (case insensitive)"},
        ]

    def create_params(self):
        return [
            {'name': 'name',
             'type': 'string',
             'required': True,
             'synopsis': 'The name of the league',
             'examples': "USAU Club Women's, MUFA Rec A Fall League M/W"},
            {'name': 'organization_id',
             'type': 'positive_integer',
             'required': True,
             'synopsis': 'ID of the organization the league is under'},
            {'name': 'sport',
             'type': 'sport',
             'required': True,
             'initial': 'ultimate',
             'synopsis': 'The sport for the league'}, 
            {'name': 'gender',
             'required': True,
             'type': 'gender',
             'synopsis': 'The gender of the league'}
        ]


full_spec = {
    'groups': [
        {'name': "Leagues",
         'synopsis': "",
         'description': "",
         'resources': [
             {'name': "Organization",
              'methods':[
                  {'synopsis': "Get a list of organizations",
                   'HTTP_method': "GET",
                   'URI': "/organizations/",
                   'requires_auth': False,
                   'parameters': OrganizationParams().get_list_params()
                  },
                  {'synopsis': "Get an organization",
                   'HTTP_method': "GET",
                   'URI': "/organizations/{organization_id}/",
                   'requires_auth': False,
                   'parameters': OrganizationParams().get_detail_params()
                  },
                  {'synopsis': "Update an organization",
                   'HTTP_method': "PUT",
                   'URI': "/organizations/{organization_id}/",
                   'requires_auth': True,
                   'parameters': OrganizationParams().get_update_params()
                  },
                  {'synopsis': "Create an organization",
                   'HTTP_method': "POST",
                   'URI': "/organizations/",
                   'requires_auth': True,
                   'parameters': OrganizationParams().get_create_params()
                  },
                  {'synopsis': "Delete an organization",
                   'HTTP_method': "DELETE",
                   'URI': "/organizations/{organization_id}/",
                   'requires_auth': True,
                   'parameters': OrganizationParams().get_delete_params()
                  }
              ] # End Method List for Organization
             },
             {'name': "League",
              'description': "Each League consists of one or more seasons, and every League is owned by a single organization.",
              'methods':[
                  {'synopsis': "Get a list of leagues",
                   'HTTP_method': "GET",
                   'URI': "/leagues/",
                   'requires_auth': False,
                   'parameters': LeagueParams().get_list_params()
                  },
                  {'synopsis': "Get a league",
                   'HTTP_method': "GET",
                   'URI': "/leagues/{league_id}/",
                   'requires_auth': False,
                   'parameters': LeagueParams().get_detail_params()
                  },
                  {'synopsis': "Update a league",
                   'HTTP_method': "PUT",
                   'URI': "/leagues/{league_id}/",
                   'requires_auth': True,
                   'parameters': LeagueParams().get_update_params()
                  },
                  {'synopsis': "Create a league",
                   'HTTP_method': "POST",
                   'URI': "/leagues/",
                   'requires_auth': True,
                   'parameters': LeagueParams().get_create_params()
                  },
                  {'synopsis': "Delete a league",
                   'HTTP_method': "DELETE",
                   'URI': "/leagues/{league_id}/",
                   'requires_auth': True,
                   'parameters': LeagueParams().get_delete_params()
                  }
              ] # End Method List for League
             },
         ] # End Resource List for Leagues
        },
    ] # end of groups list
}

full_spec_indented = simplejson.dumps(full_spec, indent=4, ensure_ascii=False)
