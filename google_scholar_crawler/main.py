import json
from datetime import datetime
import os
import sys
from urllib.parse import parse_qs, urlparse


def get_scholar_id() -> str:
    value = os.environ.get('GOOGLE_SCHOLAR_ID', '').strip()
    if value.startswith(('http://', 'https://')):
        value = parse_qs(urlparse(value).query).get('user', [''])[0]
    return value.strip()


scholar_id = get_scholar_id()
if not scholar_id:
    print('::notice::GOOGLE_SCHOLAR_ID is empty; citation update skipped.')
    sys.exit(0)

try:
    from scholarly import scholarly

    author: dict = scholarly.search_author_id(scholar_id)
    scholarly.fill(author, sections=['basics', 'indices', 'counts', 'publications'])
except Exception as error:
    print(
        '::warning title=Google Scholar data unavailable::'
        'Could not fetch a public Google Scholar profile; citation update skipped. '
        f'{type(error).__name__}: {error}'
    )
    sys.exit(0)

author['updated'] = str(datetime.now())
author['publications'] = {v['author_pub_id']: v for v in author['publications']}
print(json.dumps(author, indent=2))
os.makedirs('results', exist_ok=True)
with open('results/gs_data.json', 'w') as outfile:
    json.dump(author, outfile, ensure_ascii=False)

shieldio_data = {
    "schemaVersion": 1,
    "label": "citations",
    "message": f"{author['citedby']}",
}
with open('results/gs_data_shieldsio.json', 'w') as outfile:
    json.dump(shieldio_data, outfile, ensure_ascii=False)
