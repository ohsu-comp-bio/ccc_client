usage: ccc_client [-h] [--debug] [--host HOST] [--port PORT] [--help-long]
                  [--version]
                  {dts,app-repo,exec-engine,elasticsearch} ...

CCC client

optional arguments:
  -h, --help            show this help message and exit
  --debug               debug flag
  --host HOST           host
  --port PORT           port
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
                           --filepath FILEPATH [FILEPATH ...] --user USER
                           --site {central,dfci,ohsu,oicr}

optional arguments:
  --filepath FILEPATH [FILEPATH ...], -f FILEPATH [FILEPATH ...]
                        name of file(s) or pattern to glob on
  --user USER, -u USER  site user
  --site {central,dfci,ohsu,oicr}, -s {central,dfci,ohsu,oicr}
                        site the data resides at

-------
| put |
-------
usage: ccc_client dts put [-h] [--debug] [--host HOST] [--port PORT]
                          --filepath FILEPATH [FILEPATH ...] --user USER
                          --site {central,dfci,ohsu,oicr}

optional arguments:
  --filepath FILEPATH [FILEPATH ...], -f FILEPATH [FILEPATH ...]
                        name of file(s) or pattern to glob on
  --user USER, -u USER  user identity
  --site {central,dfci,ohsu,oicr}, -s {central,dfci,ohsu,oicr}
                        site the data resides at

-------
| get |
-------
usage: ccc_client dts get [-h] [--debug] [--host HOST] [--port PORT] --cccId
                          CCCID [CCCID ...]

optional arguments:
  --cccId CCCID [CCCID ...]
                        cccId entry to GET

----------
| delete |
----------
usage: ccc_client dts delete [-h] [--debug] [--host HOST] [--port PORT]
                             --cccId CCCID [CCCID ...]

optional arguments:
  --cccId CCCID [CCCID ...]
                        cccId entry to DELETE

---------------
| infer-cccId |
---------------
usage: ccc_client dts infer-cccId [-h] [--debug] [--host HOST] [--port PORT]
                                  --filepath FILEPATH [FILEPATH ...]
                                  [--strategy {MD5,SHA-1}]

optional arguments:
  --filepath FILEPATH [FILEPATH ...], -f FILEPATH [FILEPATH ...]
                        name of file(s) or pattern to glob on
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
                               [--metadata METADATA] [--imageId IMAGEID]

optional arguments:
  --metadata METADATA, -m METADATA
                        tool metadata
  --imageId IMAGEID, -i IMAGEID
                        docker image id

-------
| get |
-------
usage: ccc_client app-repo get [-h] [--debug] [--host HOST] [--port PORT]
                               [--imageId IMAGEID]

optional arguments:
  --imageId IMAGEID, -i IMAGEID
                        docker image id

----------
| delete |
----------
usage: ccc_client app-repo delete [-h] [--debug] [--host HOST] [--port PORT]
                                  [--imageId IMAGEID]

optional arguments:
  --imageId IMAGEID, -i IMAGEID
                        docker image id

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
                                     [--port PORT] [--wdlSource WDLSOURCE]
                                     [--workflowInputs WORKFLOWINPUTS]
                                     [--workflowOptions WORKFLOWOPTIONS]

optional arguments:
  --wdlSource WDLSOURCE, -s WDLSOURCE
                        name of file or path
  --workflowInputs WORKFLOWINPUTS, -i WORKFLOWINPUTS
                        name of docker image
  --workflowOptions WORKFLOWOPTIONS, -o WORKFLOWOPTIONS
                        docker image version tag

----------
| status |
----------
usage: ccc_client exec-engine status [-h] [--debug] [--host HOST]
                                     [--port PORT] [--workflowId WORKFLOWID]

optional arguments:
  --workflowId WORKFLOWID, -i WORKFLOWID
                        workflow uuid

-----------
| outputs |
-----------
usage: ccc_client exec-engine outputs [-h] [--debug] [--host HOST]
                                      [--port PORT] [--workflowId WORKFLOWID]

optional arguments:
  --workflowId WORKFLOWID, -i WORKFLOWID
                        workflow uuid

------------
| metadata |
------------
usage: ccc_client exec-engine metadata [-h] [--debug] [--host HOST]
                                       [--port PORT] [--workflowId WORKFLOWID]

optional arguments:
  --workflowId WORKFLOWID, -i WORKFLOWID
                        workflow uuid

============================================================
elasticsearch
============================================================
usage: ccc_client_dev.py elasticsearch [-h]
                                       {query,publish-batch,publish-resource}
                                       ...

action:
  {query,publish-batch,publish-resource}

---------
| query |
---------
usage: ccc_client_dev.py elasticsearch query [-h] [--debug] [--host HOST]
                                             [--port PORT] [--token TOKEN]
                                             [--domain {patient,specimen,sample,resource}]
                                             [--query-terms QUERY_TERMS [QUERY_TERMS ...]]

optional arguments:
  --token TOKEN, -T TOKEN
                        auth token
  --domain {patient,specimen,sample,resource}, -d {patient,specimen,sample,resource}
                        target domain of query
  --query-terms QUERY_TERMS [QUERY_TERMS ...], -q QUERY_TERMS [QUERY_TERMS ...]
                        The search terms on which to query. Can be specified
                        multiple times. Should be supplied in the form
                        'FieldName:Term'

-----------------
| publish-batch |
-----------------
usage: ccc_client_dev.py elasticsearch publish-batch [-h] [--debug]
                                                     [--host HOST]
                                                     [--port PORT]
                                                     [--token TOKEN]
                                                     [--tsv TSV]
                                                     [--site {central,dfci,ohsu,oicr}]
                                                     [--user USER]
                                                     [--project PROJECT]
                                                     [--domain {patient,specimen,sample,resource}]

optional arguments:
  --token TOKEN, -T TOKEN
                        auth token
  --tsv TSV, -t TSV     input tab delimited file
  --site {central,dfci,ohsu,oicr}, -s {central,dfci,ohsu,oicr}
                        site this data is associated with
  --user USER, -u USER  user identity
  --project PROJECT, -p PROJECT
                        The project this data is associated with
  --domain {patient,specimen,sample,resource}, -d {patient,specimen,sample,resource}
                        target domain to register the data to

--------------------
| publish-resource |
--------------------
usage: ccc_client_dev.py elasticsearch publish-resource [-h] [--debug]
                                                        [--host HOST]
                                                        [--port PORT]
                                                        [--token TOKEN]
                                                        [--filepath FILEPATH]
                                                        [--filetype FILETYPE]
                                                        [--inheritFrom INHERITFROM]
                                                        [--property-override PROPERTY_OVERRIDE [PROPERTY_OVERRIDE ...]]
                                                        [--site {central,dfci,ohsu,oicr}]
                                                        [--user USER]
                                                        [--project PROJECT]
                                                        [--workflowId WORKFLOWID]

optional arguments:
  --token TOKEN, -T TOKEN
                        auth token
  --filepath FILEPATH, -f FILEPATH
                        file to be registered in ES index
  --filetype FILETYPE, -t FILETYPE
                        the MIME type of the file
  --inheritFrom INHERITFROM, -i INHERITFROM
                        a cccId - if provided, the fields of this existing
                        record will be queried and applied to the incoming
                        resource. Any values provided using --property-
                        override will override these
  --property-override PROPERTY_OVERRIDE [PROPERTY_OVERRIDE ...], -o PROPERTY_OVERRIDE [PROPERTY_OVERRIDE ...]
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

