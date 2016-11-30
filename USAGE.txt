usage: ccc_client [-h] [--help-long] [--version]
                  {dts,exec-engine,app-repo,dcs} ...

CCC client

optional arguments:
  -h, --help            show this help message and exit
  --help-long           Show help message for all services and actions
  --version             show program's version number and exit

service:
  {dts,exec-engine,app-repo,dcs}

============================================================
dts
============================================================
usage: ccc_client dts [-h] {get,infer-cccId,put,query,post,delete} ...

action:
  {get,infer-cccId,put,query,post,delete}

-------
| get |
-------
usage: ccc_client dts get [-h] [--debug] [--host HOST] [--port PORT]
                          [--authToken AUTHTOKEN]
                          cccId [cccId ...]

positional arguments:
  cccId                 cccId entry to GET

---------------
| infer-cccId |
---------------
usage: ccc_client dts infer-cccId [--strategy {MD5,SHA-1}] [-h] [--debug]
                                  [--host HOST] [--port PORT]
                                  [--authToken AUTHTOKEN]
                                  filepath [filepath ...]

positional arguments:
  filepath              name of file(s) or pattern to glob on

optional arguments:
  --port PORT           port
  --authToken AUTHTOKEN, -T AUTHTOKEN
                        authorization token

-------
| put |
-------
usage: ccc_client dts put --filepath FILEPATH [--user USER] --site
                          {central,dfci,ohsu,oicr}
                          [{central,dfci,ohsu,oicr} ...] --cccId CCCID [-h]
                          [--debug] [--host HOST] [--port PORT]
                          [--authToken AUTHTOKEN]

optional arguments:
                        cccId entry to update
  -h, --help            show this help message and exit
  --debug               debug flag
  --host HOST           host
  --port PORT           port
  --authToken AUTHTOKEN, -T AUTHTOKEN
                        authorization token

---------
| query |
---------
usage: ccc_client dts query --site {central,dfci,ohsu,oicr} [-h] [--debug]
                            [--host HOST] [--port PORT]
                            [--authToken AUTHTOKEN]
                            filepath [filepath ...] query_terms
                            [query_terms ...]

positional arguments:
  filepath              name of file(s) and/or pattern(s) to glob on
  query_terms           The search terms on which to query. Can be specified
                        multiple times. Should be supplied in the form
                        'FieldName:Term'

optional arguments:
  --authToken AUTHTOKEN, -T AUTHTOKEN
                        authorization token

--------
| post |
--------
usage: ccc_client dts post --filepath FILEPATH [FILEPATH ...] [--user USER]
                           --site {central,dfci,ohsu,oicr}
                           [{central,dfci,ohsu,oicr} ...] [--cccId CCCID] [-h]
                           [--debug] [--host HOST] [--port PORT]
                           [--authToken AUTHTOKEN]

optional arguments:
                        cccId; if not given one will be generated
                        automatically
  -h, --help            show this help message and exit
  --debug               debug flag
  --host HOST           host
  --port PORT           port
  --authToken AUTHTOKEN, -T AUTHTOKEN
                        authorization token

----------
| delete |
----------
usage: ccc_client dts delete [-h] [--debug] [--host HOST] [--port PORT]
                             [--authToken AUTHTOKEN]
                             cccId [cccId ...]

positional arguments:
  cccId                 cccId entry to DELETE

============================================================
exec-engine
============================================================
usage: ccc_client exec-engine [-h] {status,outputs,query,submit,metadata} ...

action:
  {status,outputs,query,submit,metadata}

----------
| status |
----------
usage: ccc_client exec-engine status [-h] [--debug] [--host HOST]
                                     [--port PORT] [--authToken AUTHTOKEN]
                                     workflowId [workflowId ...]

positional arguments:
  workflowId            workflow uuid

-----------
| outputs |
-----------
usage: ccc_client exec-engine outputs [-h] [--debug] [--host HOST]
                                      [--port PORT] [--authToken AUTHTOKEN]
                                      workflowId [workflowId ...]

positional arguments:
  workflowId            workflow uuid

---------
| query |
---------
usage: ccc_client exec-engine query [-h] [--debug] [--host HOST] [--port PORT]
                                    [--authToken AUTHTOKEN]
                                    query_terms [query_terms ...]

positional arguments:
  query_terms           The search terms on which to query. Can be specified
                        multiple times. Should be supplied in the form
                        'FieldName:Term'. Possible field names: name, id,
                        status, start, end, page, pagesize

----------
| submit |
----------
usage: ccc_client exec-engine submit --wdlSource WDLSOURCE --workflowInputs
                                     WORKFLOWINPUTS [WORKFLOWINPUTS ...]
                                     [--workflowOptions WORKFLOWOPTIONS] [-h]
                                     [--debug] [--host HOST] [--port PORT]
                                     [--authToken AUTHTOKEN]

optional arguments:
  -h, --help            show this help message and exit
  --debug               debug flag
  --host HOST           host
  --port PORT           port
  --authToken AUTHTOKEN, -T AUTHTOKEN
                        authorization token

------------
| metadata |
------------
usage: ccc_client exec-engine metadata [-h] [--debug] [--host HOST]
                                       [--port PORT] [--authToken AUTHTOKEN]
                                       workflowId [workflowId ...]

positional arguments:
  workflowId            workflow uuid

============================================================
app-repo
============================================================
usage: ccc_client app-repo [-h]
                           {delete-metadata,get-metadata,upload-image,list-tools,upload-metadata,update-metadata}
                           ...

action:
  {delete-metadata,get-metadata,upload-image,list-tools,upload-metadata,update-metadata}

-------------------
| delete-metadata |
-------------------
usage: ccc_client app-repo delete-metadata [-h] [--debug] [--host HOST]
                                           [--port PORT]
                                           [--authToken AUTHTOKEN]
                                           imageId

positional arguments:
  imageId               docker image id

----------------
| get-metadata |
----------------
usage: ccc_client app-repo get-metadata [-h] [--debug] [--host HOST]
                                        [--port PORT] [--authToken AUTHTOKEN]
                                        imageIdOrName

positional arguments:
  imageIdOrName         docker image id or name

----------------
| upload-image |
----------------
usage: ccc_client app-repo upload-image [--imageBlob IMAGEBLOB]
                                        [--imageName IMAGENAME]
                                        [--imageTag IMAGETAG]
                                        [--metadata METADATA] [-h] [--debug]
                                        [--host HOST] [--port PORT]
                                        [--authToken AUTHTOKEN]

optional arguments:
  --metadata METADATA, -m METADATA
                        tool metadata; can be a filepath or json string
  -h, --help            show this help message and exit
  --debug               debug flag
  --host HOST           host
  --port PORT           port
  --authToken AUTHTOKEN, -T AUTHTOKEN
                        authorization token

--------------
| list-tools |
--------------
usage: ccc_client app-repo list-tools [-h] [--debug] [--host HOST]
                                      [--port PORT] [--authToken AUTHTOKEN]

-------------------
| upload-metadata |
-------------------
usage: ccc_client app-repo upload-metadata --metadata METADATA
                                           [--imageId IMAGEID] [-h] [--debug]
                                           [--host HOST] [--port PORT]
                                           [--authToken AUTHTOKEN]

optional arguments:
  --host HOST           host
  --port PORT           port
  --authToken AUTHTOKEN, -T AUTHTOKEN
                        authorization token

-------------------
| update-metadata |
-------------------
usage: ccc_client app-repo update-metadata --metadata METADATA
                                           [--imageId IMAGEID] [-h] [--debug]
                                           [--host HOST] [--port PORT]
                                           [--authToken AUTHTOKEN]

optional arguments:
  --host HOST           host
  --port PORT           port
  --authToken AUTHTOKEN, -T AUTHTOKEN
                        authorization token

============================================================
dcs
============================================================
usage: ccc_client dcs [-h]
                      {delete-link,delete-set,find-common-sets,list-resources,create-link,list-sets}
                      ...

action:
  {delete-link,delete-set,find-common-sets,list-resources,create-link,list-sets}

---------------
| delete-link |
---------------
usage: ccc_client dcs delete-link --setId SETID [--cccId CCCID [CCCID ...]]
                                  [-h] [--debug] [--host HOST] [--port PORT]
                                  [--authToken AUTHTOKEN]

optional arguments:
  --host HOST           host
  --port PORT           port
  --authToken AUTHTOKEN, -T AUTHTOKEN
                        authorization token

--------------
| delete-set |
--------------
usage: ccc_client dcs delete-set [-h] [--debug] [--host HOST] [--port PORT]
                                 [--authToken AUTHTOKEN]
                                 setId [setId ...]

positional arguments:
  setId                 UUID(s) of resource set(s) to delete

--------------------
| find-common-sets |
--------------------
usage: ccc_client dcs find-common-sets [-h] [--debug] [--host HOST]
                                       [--port PORT] [--authToken AUTHTOKEN]
                                       cccId [cccId ...]

positional arguments:
  cccId                 CCC_IDs to search

------------------
| list-resources |
------------------
usage: ccc_client dcs list-resources [-h] [--debug] [--host HOST]
                                     [--port PORT] [--authToken AUTHTOKEN]
                                     setId

positional arguments:
  setId                 UUID of resource set

---------------
| create-link |
---------------
usage: ccc_client dcs create-link --setId SETID [--cccId CCCID [CCCID ...]]
                                  [-h] [--debug] [--host HOST] [--port PORT]
                                  [--authToken AUTHTOKEN]

optional arguments:
  --host HOST           host
  --port PORT           port
  --authToken AUTHTOKEN, -T AUTHTOKEN
                        authorization token

-------------
| list-sets |
-------------
usage: ccc_client dcs list-sets [-h] [--debug] [--host HOST] [--port PORT]
                                [--authToken AUTHTOKEN]
                                cccId

positional arguments:
  cccId                 CCC_ID of resource

