usage: ccc_client_dev.py [-h] [--host HOST] [--port PORT] [--version]
                         [--debug] [--help-long]
                         {dts,app-repo,exec-engine} ...

CCC client

optional arguments:
  -h, --help            show this help message and exit
  --host HOST           host
  --port PORT           port
  --version             show program's version number and exit
  --debug               debug flag
  --help-long           Show help message for all services and actions

service:
  {dts,app-repo,exec-engine}

============================================================
dts
============================================================
usage: ccc_client_dev.py dts [-h] {post,get,delete} ...

action:
  {post,get,delete}

--------
| post |
--------
usage: ccc_client_dev.py dts post [-h] [--host HOST] [--port PORT] [--version]
                                  [--debug] [--help-long] --filepath FILEPATH
                                  [FILEPATH ...] --user USER --site
                                  {central,dfci,ohsu,oicr}

optional arguments:
  --filepath FILEPATH [FILEPATH ...], -f FILEPATH [FILEPATH ...]
                        name of file(s) or pattern to glob on
  --user USER, -u USER  site user
  --site {central,dfci,ohsu,oicr}, -s {central,dfci,ohsu,oicr}
                        site the data resides at

-------
| get |
-------
usage: ccc_client_dev.py dts get [-h] [--host HOST] [--port PORT] [--version]
                                 [--debug] [--help-long] --cccId CCCID
                                 [CCCID ...]

optional arguments:
  --cccId CCCID [CCCID ...]
                        cccId entry to GET

----------
| delete |
----------
usage: ccc_client_dev.py dts delete [-h] [--host HOST] [--port PORT]
                                    [--version] [--debug] [--help-long]
                                    --cccId CCCID [CCCID ...]

optional arguments:
  --cccId CCCID [CCCID ...]
                        cccId entry to DELETE

============================================================
app-repo
============================================================
usage: ccc_client_dev.py app-repo [-h] {post,put,get,delete} ...

action:
  {post,put,get,delete}

--------
| post |
--------
usage: ccc_client_dev.py app-repo post [-h] [--host HOST] [--port PORT]
                                       [--version] [--debug] [--help-long]
                                       [--imageBlob IMAGEBLOB]
                                       [--imageName IMAGENAME]
                                       [--imageTag IMAGETAG]
                                       [--metadata METADATA]

optional arguments:
  --imageBlob IMAGEBLOB, -b IMAGEBLOB
                        name of file or path
  --imageName IMAGENAME, -n IMAGENAME
                        name of docker image
  --imageTag IMAGETAG, -t IMAGETAG
                        docker image version tag
  --metadata METADATA, -m METADATA
                        tool metadata

-------
| put |
-------
usage: ccc_client_dev.py app-repo put [-h] [--host HOST] [--port PORT]
                                      [--version] [--debug] [--help-long]
                                      [--metadata METADATA]
                                      [--imageId IMAGEID]

optional arguments:
  --metadata METADATA, -m METADATA
                        tool metadata
  --imageId IMAGEID, -i IMAGEID
                        docker image id

-------
| get |
-------
usage: ccc_client_dev.py app-repo get [-h] [--host HOST] [--port PORT]
                                      [--version] [--debug] [--help-long]
                                      [--imageId IMAGEID]

optional arguments:
  --imageId IMAGEID, -i IMAGEID
                        docker image id

----------
| delete |
----------
usage: ccc_client_dev.py app-repo delete [-h] [--host HOST] [--port PORT]
                                         [--version] [--debug] [--help-long]
                                         [--imageId IMAGEID]

optional arguments:
  --imageId IMAGEID, -i IMAGEID
                        docker image id

============================================================
exec-engine
============================================================
usage: ccc_client_dev.py exec-engine [-h] {submit,status,outputs,metadata} ...

action:
  {submit,status,outputs,metadata}

----------
| submit |
----------
usage: ccc_client_dev.py exec-engine submit [-h] [--host HOST] [--port PORT]
                                            [--version] [--debug]
                                            [--help-long]
                                            [--wdlSource WDLSOURCE]
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
usage: ccc_client_dev.py exec-engine status [-h] [--host HOST] [--port PORT]
                                            [--version] [--debug]
                                            [--help-long]
                                            [--workflowId WORKFLOWID]

optional arguments:
  --workflowId WORKFLOWID, -i WORKFLOWID
                        workflow uuid

-----------
| outputs |
-----------
usage: ccc_client_dev.py exec-engine outputs [-h] [--host HOST] [--port PORT]
                                             [--version] [--debug]
                                             [--help-long]
                                             [--workflowId WORKFLOWID]

optional arguments:
  --workflowId WORKFLOWID, -i WORKFLOWID
                        workflow uuid

------------
| metadata |
------------
usage: ccc_client_dev.py exec-engine metadata [-h] [--host HOST] [--port PORT]
                                              [--version] [--debug]
                                              [--help-long]
                                              [--workflowId WORKFLOWID]

optional arguments:
  --workflowId WORKFLOWID, -i WORKFLOWID
                        workflow uuid

