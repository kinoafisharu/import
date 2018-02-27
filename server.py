from flask import Flask, render_template, Response
import tempfile
from werkzeug.contrib.cache import FileSystemCache
from parse_site.parser_elcom import get_output_elcom
from parse_site.parser_merg import get_output_merg
import json


ONE_DAY = 60 * 60 * 24

app = Flask(__name__)
tmp_dir = tempfile.mkdtemp()
cache = FileSystemCache(cache_dir=tmp_dir)


def products_info_from_cache():
    products_info = cache.get('products_info')
    if products_info is None:
        products_info = get_output_merg()
        cache.set('products_info', products_info, timeout=ONE_DAY)
    return products_info


@app.route('/api/')
def get_api():
    return Response(json.dumps(products_info_from_cache(),
                               indent=2,
                               ensure_ascii=False),
                    content_type='application/json; charset=utf-8')


if __name__ == "__main__":
    app.run()