This tool provides a command line interface to services within the CCC, along with python libraries suitable for direct use from other python scripts.  Documentation of the command line options is below.


usage: ccc_client [-h] [--debug] [--host HOST] [--port PORT]
                  [--authToken AUTHTOKEN] [--help-long] [--version]
                  {dts,app-repo,exec-engine,elasticsearch} ...

CCC client

optional arguments:
  -h, --help            show this help message and exit
  --debug               debug flag
  --host HOST           host
  --port PORT           port
  --authToken AUTHTOKEN, -T AUTHTOKEN
                        authorization token
  --help-long           Show help message for all services and actions
  --version             show program's version number and exit

service:
  {dts,app-repo,exec-engine,elasticsearch}

============================================================
dts
============================================================
usage: ccc_client dts [-h] {post,put,get,delete,infer-cccId} ...

action:
  {post,put,get,delete,infer-cccId}

--------
| post |
--------
usage: ccc_client dts post [-h] [--debug] [--host HOST] [--port PORT]
                           [--authToken AUTHTOKEN] --filepath FILEPATH
                           [FILEPATH ...] [--user USER] --site
                           {central,dfci,ohsu,oicr}
                           [{central,dfci,ohsu,oicr} ...] [--cccId CCCID]

optional arguments:
  --filepath FILEPATH [FILEPATH ...], -f FILEPATH [FILEPATH ...]
                        name of file(s) or pattern to glob on
  --user USER, -u USER  user identity
  --site {central,dfci,ohsu,oicr} [{central,dfci,ohsu,oicr} ...], -s {central,dfci,ohsu,oicr} [{central,dfci,ohsu,oicr} ...]
                        site the data resides at
  --cccId CCCID         cccId; if not given one will be generated
                        automatically

-------
| put |
-------
usage: ccc_client dts put [-h] [--debug] [--host HOST] [--port PORT]
                          [--authToken AUTHTOKEN] --cccId CCCID --filepath
                          FILEPATH [--user USER] --site
                          {central,dfci,ohsu,oicr}
                          [{central,dfci,ohsu,oicr} ...]

optional arguments:
  --cccId CCCID         cccId entry to update
  --filepath FILEPATH, -f FILEPATH
                        filepath
  --user USER, -u USER  site user
  --site {central,dfci,ohsu,oicr} [{central,dfci,ohsu,oicr} ...], -s {central,dfci,ohsu,oicr} [{central,dfci,ohsu,oicr} ...]
                        site the data resides at

-------
| get |
-------
usage: ccc_client dts get [-h] [--debug] [--host HOST] [--port PORT]
                          [--authToken AUTHTOKEN]
                          cccId [cccId ...]

positional arguments:
  cccId                 cccId entry to GET

----------
| delete |
----------
usage: ccc_client dts delete [-h] [--debug] [--host HOST] [--port PORT]
                             [--authToken AUTHTOKEN]
                             cccId [cccId ...]

positional arguments:
  cccId                 cccId entry to DELETE

---------------
| infer-cccId |
---------------
usage: ccc_client dts infer-cccId [-h] [--debug] [--host HOST] [--port PORT]
                                  [--authToken AUTHTOKEN]
                                  [--strategy {MD5,SHA-1}]
                                  filepath [filepath ...]

positional arguments:
  filepath              name of file(s) or pattern to glob on

optional arguments:
  --strategy {MD5,SHA-1}, -s {MD5,SHA-1}
                        hashing strategy to use to generate the cccId
                        (default: SHA-1)

============================================================
app-repo
============================================================
usage: ccc_client app-repo [-h] {post,put,get,delete} ...

action:
  {post,put,get,delete}

--------
| post |
--------
usage: ccc_client app-repo post [-h] [--debug] [--host HOST] [--port PORT]
                                [--authToken AUTHTOKEN]
                                [--imageBlob IMAGEBLOB]
                                [--imageName IMAGENAME] [--imageTag IMAGETAG]
                                [--metadata METADATA]

optional arguments:
  --imageBlob IMAGEBLOB, -b IMAGEBLOB
                        name of file or path
  --imageName IMAGENAME, -n IMAGENAME
                        name of docker image
  --imageTag IMAGETAG, -t IMAGETAG
                        docker image version tag
  --metadata METADATA, -m METADATA
                        tool metadata; can be a filepath or json string

-------
| put |
-------
usage: ccc_client app-repo put [-h] [--debug] [--host HOST] [--port PORT]
                               [--authToken AUTHTOKEN] --metadata METADATA
                               [--imageId IMAGEID]

optional arguments:
  --metadata METADATA, -m METADATA
                        tool metadata
  --imageId IMAGEID, -i IMAGEID
                        docker image id

-------
| get |
-------
usage: ccc_client app-repo get [-h] [--debug] [--host HOST] [--port PORT]
                               [--authToken AUTHTOKEN]
                               imageId

positional arguments:
  imageId               docker image id or name

----------
| delete |
----------
usage: ccc_client app-repo delete [-h] [--debug] [--host HOST] [--port PORT]
                                  [--authToken AUTHTOKEN]
                                  imageId

positional arguments:
  imageId               docker image id

============================================================
exec-engine
============================================================
usage: ccc_client exec-engine [-h] {submit,status,outputs,metadata} ...

action:
  {submit,status,outputs,metadata}

----------
| submit |
----------
usage: ccc_client exec-engine submit [-h] [--debug] [--host HOST]
                                     [--port PORT] [--authToken AUTHTOKEN]
                                     --wdlSource WDLSOURCE --workflowInputs
                                     WORKFLOWINPUTS [WORKFLOWINPUTS ...]
                                     [--workflowOptions WORKFLOWOPTIONS]

optional arguments:
  --wdlSource WDLSOURCE, -s WDLSOURCE
                        WDL source file defining a workflow
  --workflowInputs WORKFLOWINPUTS [WORKFLOWINPUTS ...], -i WORKFLOWINPUTS [WORKFLOWINPUTS ...]
                        json file(s) defining workflow input mappings
  --workflowOptions WORKFLOWOPTIONS, -o WORKFLOWOPTIONS
                        workflow options

----------
| status |
----------
usage: ccc_client exec-engine status [-h] [--debug] [--host HOST]
                                     [--port PORT] [--authToken AUTHTOKEN]
                                     workflowId

positional arguments:
  workflowId            workflow uuid

-----------
| outputs |
-----------
usage: ccc_client exec-engine outputs [-h] [--debug] [--host HOST]
                                      [--port PORT] [--authToken AUTHTOKEN]
                                      workflowId

positional arguments:
  workflowId            workflow uuid

------------
| metadata |
------------
usage: ccc_client exec-engine metadata [-h] [--debug] [--host HOST]
                                       [--port PORT] [--authToken AUTHTOKEN]
                                       workflowId

positional arguments:
  workflowId            workflow uuid

============================================================
elasticsearch
============================================================
usage: ccc_client elasticsearch [-h]
                                {query,publish-batch,publish-resource} ...

action:
  {query,publish-batch,publish-resource}

---------
| query |
---------
usage: ccc_client elasticsearch query [-h] [--debug] [--host HOST]
                                      [--port PORT] [--authToken AUTHTOKEN]
                                      [--domain {patient,specimen,sample,resource}]
                                      --query-terms QUERY_TERMS
                                      [QUERY_TERMS ...]

optional arguments:
  --domain {patient,specimen,sample,resource}, -d {patient,specimen,sample,resource}
                        target domain of query
  --query-terms QUERY_TERMS [QUERY_TERMS ...], -q QUERY_TERMS [QUERY_TERMS ...]
                        The search terms on which to query. Can be specified
                        multiple times. Should be supplied in the form
                        'FieldName:Term'

-----------------
| publish-batch |
-----------------
usage: ccc_client elasticsearch publish-batch [-h] [--debug] [--host HOST]
                                              [--port PORT]
                                              [--authToken AUTHTOKEN] --tsv
                                              TSV
                                              [--site {central,dfci,ohsu,oicr}]
                                              [--user USER]
                                              [--project PROJECT]
                                              [--domain {patient,specimen,sample,resource}]
                                              [--domainJson DOMAINJSON]
                                              [--mock] [--skipDtsRegistration]

optional arguments:
  --tsv TSV, -t TSV     input tab delimited file
  --site {central,dfci,ohsu,oicr}, -s {central,dfci,ohsu,oicr}
                        site this data is associated with
  --user USER, -u USER  user identity
  --project PROJECT, -p PROJECT
                        The project this data is associated with
  --domain {patient,specimen,sample,resource}, -d {patient,specimen,sample,resource}
                        target domain to register the data to
  --domainJson DOMAINJSON, -D DOMAINJSON
                        this is the path to an alternate file describing the
                        domains/fields to use for import.
  --mock                perform a mock operation, which runs your input
                        through the normal code path, but outputs the JSON
                        that would otherwise be posted to elasticsearch,
                        without actually sending it
  --skipDtsRegistration
                        skip any attempt to register or validate CCC Ids and
                        filepaths with the DTS

--------------------
| publish-resource |
--------------------
usage: ccc_client elasticsearch publish-resource [-h] [--debug] [--host HOST]
                                                 [--port PORT]
                                                 [--authToken AUTHTOKEN]
                                                 --filepath FILEPATH
                                                 [--mimeType MIMETYPE]
                                                 [--inheritFrom INHERITFROM]
                                                 [--propertyOverride PROPERTYOVERRIDE [PROPERTYOVERRIDE ...]]
                                                 [--site {central,dfci,ohsu,oicr}]
                                                 [--user USER]
                                                 [--project PROJECT]
                                                 [--workflowId WORKFLOWID]
                                                 [--domainJson DOMAINJSON]
                                                 [--mock]
                                                 [--skipDtsRegistration]

optional arguments:
  --filepath FILEPATH, -f FILEPATH
                        file to be registered in ES index
  --mimeType MIMETYPE, -t MIMETYPE
                        the MIME type of the file
  --inheritFrom INHERITFROM, -i INHERITFROM
                        a cccId - if provided, the fields of this existing
                        record will be queried and applied to the incoming
                        resource. Any values provided using --propertyOverride
                        will override these
  --propertyOverride PROPERTYOVERRIDE [PROPERTYOVERRIDE ...], -o PROPERTYOVERRIDE [PROPERTYOVERRIDE ...]
                        One or more fields to apply to the incoming resource.
                        The values should be supplied in the form
                        'FieldName:Value'
  --site {central,dfci,ohsu,oicr}, -s {central,dfci,ohsu,oicr}
                        site this file is associated with
  --user USER, -u USER  user identity
  --project PROJECT, -p PROJECT
                        The project this file is associated with
  --workflowId WORKFLOWID, -w WORKFLOWID
                        The workflow this file was generated by
  --domainJson DOMAINJSON, -D DOMAINJSON
                        this is the path to an alternate file describing the
                        domains/fields to use for import.
  --mock                perform a mock operation, which runs your input
                        through the normal code path, but outputs the JSON
                        that would otherwise be posted to elasticsearch,
                        without actually sending it
  --skipDtsRegistration
                        skip any attempt to register or validate CCC Ids and
                        filepaths with the DTS

