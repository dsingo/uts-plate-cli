import requests as r
from getpass import getpass
from bs4 import BeautifulSoup as bs
from functools import partial
from io import StringIO, BytesIO
import zipfile
import os
from pathlib import Path

host = 'https://plate.it.uts.edu.au/'

auth=(input('Student Id: '), getpass('Password: '))


def parse_subjects(a_tag, auth_token):
    link = a_tag.get("href")
    cookies = {'JSESSIONID':auth_token}
    subject = link[link.find('?subjectId')+11:]
    res = r.get(f'{host}/assessments_view.action?subjectId={subject}', cookies=cookies, verify='plate.pem', auth=auth)
    soup = bs(res.text)
    return {
        'name': a_tag.string,
        'link': a_tag.get('href'),
        'subjectId': subject,
        'assessments': [parse_assessment(x) for x in soup.find_all('tr') if parse_assessment(x) != -1]
    }

def parse_assessment(table_row):
    a_tag = table_row.find('a')
    if a_tag != None:
        return {
            'title': a_tag.text,
            'assessmentId': a_tag.get('href')[a_tag.get('href').find('assessmentId=')+13:],
            'score': table_row.contents[-4].text.replace('\n',"").replace("\t","")
        }
    else: 
        return -1


def list_assessments():
    print("Fetching Assessments... 🚚")
    res = r.get(f'{host}/index_view.action', verify='plate.pem', auth=auth)
    auth_token = res.cookies['JSESSIONID']
    soup = bs(res.text)
    subjectIds = list(filter(lambda x: '?subjectId' in x.get('href'),soup.find_all("a")))
    subjects = list(map(lambda x: parse_subjects(x, auth_token), subjectIds))
    for subject in subjects:
        print(f"📝 {subject['subjectId']}/")
        for assessment in subject['assessments']:
            print(f"\t{assessment['assessmentId']}\t\t{assessment['score']}")

def clone_assessment(path):
    assert len(path.split('/')) == 2, "Invalid Subject and Assessment Combination"
    subject, assessment = path.split('/')
    print(f"🔨 Cloning assessment into  {subject}/{assessment}/")
    res = r.get(f'{host}/assessment_view.action?subjectId={subject}&assessmentId={assessment}', verify='plate.pem', auth=auth)
    soup = bs(res.text)
    jar_files = list(filter(lambda x: '.jar' in x.get('href'), soup.find_all('a')))
    jar_files.extend(list(filter(lambda x: '.zip' in x.get('href'), soup.find_all('a'))))
    Path(f'testfiles/{subject}/{assessment}').mkdir(parents=True, exist_ok=True)
    for tag in jar_files:
        print(f"📦 Fetching {tag.text} ...")
        url = str(tag.get('href'))
        if url.startswith("/itemAttachment"):
            url = f"{host}{url}"
        file_res = r.get(url, auth=auth, verify='plate.pem')
        zip_jar = zipfile.ZipFile(BytesIO(file_res.content))
        zip_jar.extractall(f'testfiles/{subject}/{assessment}')
    print(f"✅ Done! The assessment was successfully downloaded.")

def upload_assessment(path):
    assert len(path.split('/')) == 2, "Invalid Subject and Assessment Combination"
    subject, assessment = path.split('/')
    byteFile = BytesIO()
    archive = zipfile.ZipFile(byteFile, mode="w", compression=zipfile.ZIP_DEFLATED)
    path = 'testfiles/'+path
    for root, dirs, files in os.walk(path):
        for file in files:
            archive.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(path, '.')))
    archive.close()
    files = {'upload':( 'submission.jar', byteFile.getvalue(), 'application/java-archive')}
    with open('submission.zip', 'wb') as r:
        r.write(byteFile.getvalue())
    data = {"upload":"Upload"}
    res = r.post(f'{host}/submission_upload.action?subjectId={subject}&assessmentId={assessment}', files=files, data=data, auth=auth, verify='plate.pem')
    soup = bs(res.text)
    soup
    soup.find_all('fieldset')


if __name__ == "__main__":
    list_assessments()