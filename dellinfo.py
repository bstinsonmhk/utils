#!/usr/bin/env python
import re
import suds
import uuid

def valid_servicetag(servicetag):
    # Keep me from doing something stupid...this is not a robust sanity check
    return (re.match("^[a-zA-Z0-9]{7}$",servicetag) is not None)

def get_asset_information(servicetag):
    asset_information = {}

    header_attributes = [
                            ('purchasedate','SystemShipDate'),
                            ('type', 'SystemType'),
                            ('model', 'SystemModel') 
                        ]

    entitle_attributes = [
                            ('warranty_type', 'ServiceLevelCode'),
                            ('start_date', 'StartDate'),
                            ('end_date', 'EndDate'),
                            ('days_left', 'DaysLeft'),
                            ('status', 'EntitlementType'), 
                        ]

    appurl = 'http://xserv.dell.com/services/assetservice.asmx?WSDL'

    if not valid_servicetag(servicetag):
        raise ValueError('Service Tags should be 7 Alphanumeric characters, %s does not conform' % servicetag)

    suds_client = suds.client.Client(appurl)
    result = suds_client.service.GetAssetInformation(str(uuid.uuid1()), 'dellwarrantycheck', servicetag)

    # We only have one service tag, so we know for sure we will only be returned
    # one asset
    header = result.Asset[0].AssetHeaderData
    entitle = result.Asset[0].Entitlements[0]

    for ours,theirs in header_attributes:
        asset_information[ours] = header[theirs]

    asset_information['warranties'] = []
    for warranty in entitle:
        warranty_information = {}
        for ours, theirs in entitle_attributes:
            warranty_information[ours] = warranty[theirs]
        asset_information['warranties'].append(warranty_information)

    return asset_information

