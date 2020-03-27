# UTS Plate CLI
List, download and reupload your plate code. 

Note: None of this works yet, we'll turn it into a workable command line tool in a couple days.

## Functions:
- list_assessments() Will list all subjects available on plate and their assessments
- clone_assessment(path) - Takes a path of subject/assessment and will download the files to your vscode directory (uses a placeholder directory called testfiles for testing)
- upload_assessment(path) - BROKEN Takes a path of the folder where your assessment is folder and uploads it to the equivalent subject/assessment. Eventually will return results

## Usage
So generally I just run this in interactive mode, import the libraries, define the auth and host variables before trying to debug it all.