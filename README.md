Pipelining
===============
Pipelining is a C/S structure platform aims to process files via typing simple commands. 
## automatic
Pipelining provides a lot of common functions, such as retriving infomation from sqlserver, extracting files via http or ftp, decrypting files and etc. By providing config files, processes are handled automatically, no intervention needed! All available operations are listed at the section [interfaces](#interface). 
## easy
Requests are submitted by typing `pipe publish order.yaml` The YAML called *order* specifies the sequence of operations and argments passed in. Pipelining offers several templates to make it easy to customize orders. It also allows templates overriding to repeate same works done before by changing few values (for example, path to  source files). 

## extensible
Processing are various but the platform is extensible. Coding your own handlers as inheritance of `base.WorkStation`, uploading and regestering in `settings_local.py` makes it plug-and-play. 

## trackable
Operations are recorded in `logs`, which makes it possible to track data

