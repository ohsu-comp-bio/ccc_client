usage: ccc_client_dev.py [-h] [--help-long] [--version] [--debug]
                         [--host HOST] [--port PORT]
                         {dts,app-repo,exec-engine} ...

CCC client

optional arguments:
  -h, --help            show this help message and exit
  --help-long           Show help message for all services and actions
  --version             show program's version number and exit
  --debug               debug flag
  --host HOST           host
  --port PORT           port

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
usage: ccc_client_dev.py dts post [-h] [--help-long] [--version] [--debug]
                                  [--host HOST] [--port PORT] --filepath
                                  FILEPATH [FILEPATH ...] --user USER --site
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
usage: ccc_client_dev.py dts get [-h] [--help-long] [--version] [--debug]
                                 [--host HOST] [--port PORT] --cccId CCCID
                                 [CCCID ...]

optional arguments:
  --cccId CCCID [CCCID ...]
                        cccId entry to GET

----------
| delete |
----------
usage: ccc_client_dev.py dts delete [-h] [--help-long] [--version] [--debug]
                                    [--host HOST] [--port PORT] --cccId CCCID
                                    [CCCID ...]

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
usage: ccc_client_dev.py app-repo post [-h] [--help-long] [--version]
                                       [--debug] [--host HOST] [--port PORT]
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
usage: ccc_client_dev.py app-repo put [-h] [--help-long] [--version] [--debug]
                                      [--host HOST] [--port PORT]
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
usage: ccc_client_dev.py app-repo get [-h] [--help-long] [--version] [--debug]
                                      [--host HOST] [--port PORT]
                                      [--imageId IMAGEID]

optional arguments:
  --imageId IMAGEID, -i IMAGEID
                        docker image id

----------
| delete |
----------
usage: ccc_client_dev.py app-repo delete [-h] [--help-long] [--version]
                                         [--debug] [--host HOST] [--port PORT]
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
usage: ccc_client_dev.py exec-engine submit [-h] [--help-long] [--version]
                                            [--debug] [--host HOST]
                                            [--port PORT]
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
usage: ccc_client_dev.py exec-engine status [-h] [--help-long] [--version]
                                            [--debug] [--host HOST]
                                            [--port PORT]
                                            [--workflowId WORKFLOWID]

optional arguments:
  --workflowId WORKFLOWID, -i WORKFLOWID
                        workflow uuid

-----------
| outputs |
-----------
usage: ccc_client_dev.py exec-engine outputs [-h] [--help-long] [--version]
                                             [--debug] [--host HOST]
                                             [--port PORT]
                                             [--workflowId WORKFLOWID]

optional arguments:
  --workflowId WORKFLOWID, -i WORKFLOWID
                        workflow uuid

------------
| metadata |
------------
usage: ccc_client_dev.py exec-engine metadata [-h] [--help-long] [--version]
                                              [--debug] [--host HOST]
                                              [--port PORT]
                                              [--workflowId WORKFLOWID]

optional arguments:
  --workflowId WORKFLOWID, -i WORKFLOWID
                        workflow uuid

