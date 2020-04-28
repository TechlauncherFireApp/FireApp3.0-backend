from flask import Flask
from flask_restful import reqparse, abort, Resource, fields, marshal_with, inputs
from gurobi.DataGenerator import volunteerGenerate, NumberGenerator
from gurobi.Names import firstNames, lastNames

import random
from ast import literal_eval # casts a string to a dict


# Define data input
# Validate a timeblock input
def input_timeblock(timeblock, name):
    timeblock = inputs.natural(timeblock)
    max_timeblock = 335
    if timeblock > max_timeblock:
        raise ValueError("The parameter '{}' is too large. Max is {}. You gave us: {}".format(name, max_timeblock, timeblock))
    return timeblock

# Validate an asset request input
def input_asset_req(value, name):
    # Validate that asset_list contains dictionaries
    try:
        cast_dict = literal_eval(value)
    except:
        raise ValueError("The parameter '{}' is not a dictionary. You gave us: {}".format(name, value))
    if type(cast_dict) is dict:
        # Validate asset_id key
        if 'asset_id' in cast_dict:
            inputs.positive(cast_dict['asset_id'])
        else:
            raise ValueError("The parameter 'asset_id' does not exist in the dictionary: {}".format(value))
        # Validate start_time key
        if 'start_time' in cast_dict:
            cast_dict['start_time'] = input_timeblock(cast_dict['start_time'], 'start_time')
        else:
            raise ValueError("The parameter 'start_time' does not exist in the dictionary: {}".format(value))
        # Validate start_time key
        if 'end_time' in cast_dict:
            cast_dict['end_time'] = input_timeblock(cast_dict['end_time'], 'end_time')
        else:
            raise ValueError("The parameter 'end_time' does not exist in the dictionary: {}".format(value))
        # Validate the start_time is before the end_time
        if cast_dict['start_time'] >= cast_dict['end_time']:
            raise ValueError("The start_time '{}' cannot be after the end_time '{}'".format(cast_dict['start_time'], cast_dict['end_time']))

    return cast_dict

parser = reqparse.RequestParser()
parser.add_argument('asset_list', action='append', type=input_asset_req)

# Define data output
TimeBlock = fields.Integer

position_field = {
    'position_id': fields.Integer,
    'role': fields.String, # driver | advanced | basic
    'qualifications': fields.String,
}

volunteer_field = {
    'volunteer_id': fields.Integer,
    'position_id': fields.Integer,
    'volunteer_name': fields.String,
    'role': fields.String, # driver | advanced | basic
    'qualifications': fields.String,
    'contact_info': fields.List(fields.Nested({
        'type': fields.String, # email | phone
        'detail': fields.String, # email_add | phone_no
    }))
}

volunteer_list_field = {
    'asset_id': fields.Integer,
    'asset_class': fields.String, # Enum
    'start_time': TimeBlock,
    'end_time': TimeBlock,
    'position': fields.List(fields.Nested(position_field)),
    'volunteers': fields.List(fields.Nested(volunteer_field)),
}

resource_fields = {
    'volunteer_list': fields.List(fields.Nested(volunteer_list_field)),
}


# Format the position data
def formatPosition(position, role, qualifications):
    return {
        'position_id': position,
        'role': role,
        'qualifications': qualifications,
    }


# Create and format a random Volunteer output data
def formatVolunteer(position, role):
    return {
        'volunteer_id': random.randint(0, 99),
        'position_id': position,
        'volunteer_name': firstNames[random.randint(0,len(firstNames)-1)]+" "+lastNames[random.randint(0,len(lastNames)-1)],
        'role': role,
        'qualifications': "",
        'contact_info': [{
            'type': "phone",
            'detail': NumberGenerator(),
        }]
    }


# Handle the Recommendation endpoint
class Recommendation(Resource):
    @marshal_with(resource_fields)
    def post(self):
        args = parser.parse_args()

        print(args)
        print(args["asset_list"][0])

        # TODO Call a Gurobi function
        # args["asset_list"] =  [{'asset_id': '3', 'start_time': 24, 'end_time': 36}]

        first_req = args["asset_list"][0]

        return_data = {
            'asset_id': first_req['asset_id'],
            'asset_class': "Heavy",
            'start_time': first_req['start_time'],
            'end_time': first_req['end_time'],
            'position': [
                formatPosition(1,"driver",""),
                formatPosition(2,"advanced",""),
                formatPosition(3,"advanced",""),
                formatPosition(4,"basic",""),
            ],
            'volunteers': [
                formatVolunteer(1,"driver"),
                formatVolunteer(2,"advanced"),
                formatVolunteer(3,"advanced"),
                formatVolunteer(4,"basic")
            ]
        }
        return {"volunteer_list" : [return_data]}