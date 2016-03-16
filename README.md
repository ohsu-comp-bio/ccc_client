# CCC Client

usage: ccc_client.py [-h] [--debug] [--extra-help]
                     {dts,app-repo,exec-engine} ...

CCC client

optional arguments:
  -h, --help            show this help message and exit
  --debug               debug flag
  --extra-help          Show help message for all services and actions

service:
  {dts,app-repo,exec-engine}

============================================================
dts
============================================================
usage: ccc_client.py dts [-h]
                         [--host {0.0.0.0,central-gateway.ccc.org,docker-centos7}]
                         [--port PORT]
                         {post,get,delete} ...

optional arguments:
  --host {0.0.0.0,central-gateway.ccc.org,docker-centos7}
                        host
  --port PORT           port

action:
  {post,get,delete}

--------
| post |
--------
usage: ccc_client.py dts post [-h] --filepath FILEPATH [FILEPATH ...] --user
                              USER --site {central,dfci,ohsu,oicr}

optional arguments:
  --filepath FILEPATH [FILEPATH ...], -f FILEPATH [FILEPATH ...]
                        name of file(s) or pattern to glob on
  --user USER, -u USER  site user
  --site {central,dfci,ohsu,oicr}, -s {central,dfci,ohsu,oicr}
                        site the data resides at

-------
| get |
-------
usage: ccc_client.py dts get [-h] --cccId CCCID [CCCID ...]

optional arguments:
  --cccId CCCID [CCCID ...]
                        cccId entry to GET

----------
| delete |
----------
usage: ccc_client.py dts delete [-h] --cccId CCCID [CCCID ...]

optional arguments:
  --cccId CCCID [CCCID ...]
                        cccId entry to DELETE

============================================================
app-repo
============================================================
usage: ccc_client.py app-repo [-h]
                              [--host {0.0.0.0,central-gateway.ccc.org,docker-centos7}]
                              [--port PORT]
                              {post,put,get,delete} ...

optional arguments:
  --host {0.0.0.0,central-gateway.ccc.org,docker-centos7}
                        host
  --port PORT           port

action:
  {post,put,get,delete}

--------
| post |
--------
usage: ccc_client.py app-repo post [-h] [--filepath FILEPATH]
                                   [--imageName IMAGENAME]
                                   [--imageTag IMAGETAG] [--metadata METADATA]

optional arguments:
  --filepath FILEPATH, -f FILEPATH
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
usage: ccc_client.py app-repo put [-h] [--metadata METADATA]
                                  [--imageId IMAGEID]

optional arguments:
  --metadata METADATA, -m METADATA
                        tool metadata
  --imageId IMAGEID, -i IMAGEID
                        docker image id

-------
| get |
-------
usage: ccc_client.py app-repo get [-h] [--imageId IMAGEID]

optional arguments:
  --imageId IMAGEID, -i IMAGEID
                        docker image id

----------
| delete |
----------
usage: ccc_client.py app-repo delete [-h] [--imageId IMAGEID]

optional arguments:
  --imageId IMAGEID, -i IMAGEID
                        docker image id

============================================================
exec-engine
============================================================
usage: ccc_client.py exec-engine [-h]
                                 [--host {0.0.0.0,central-gateway.ccc.org,docker-centos7}]
                                 [--port PORT]
                                 {submit,status,outputs,metadata} ...

optional arguments:
  --host {0.0.0.0,central-gateway.ccc.org,docker-centos7}
                        host
  --port PORT           port

action:
  {submit,status,outputs,metadata}

----------
| submit |
----------
usage: ccc_client.py exec-engine submit [-h] [--wdlSource WDLSOURCE]
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
usage: ccc_client.py exec-engine status [-h] [--workflowId WORKFLOWID]

optional arguments:
  --workflowId WORKFLOWID, -i WORKFLOWID
                        workflow uuid

-----------
| outputs |
-----------
usage: ccc_client.py exec-engine outputs [-h] [--workflowId WORKFLOWID]

optional arguments:
  --workflowId WORKFLOWID, -i WORKFLOWID
                        workflow uuid

------------
| metadata |
------------
usage: ccc_client.py exec-engine metadata [-h] [--workflowId WORKFLOWID]

optional arguments:
  --workflowId WORKFLOWID, -i WORKFLOWID
                        workflow uuid
