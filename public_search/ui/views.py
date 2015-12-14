
import os
from . import app, aac


from flask import g, current_app, send_from_directory, send_file, request, abort, url_for
from flask.json import jsonify

@app.teardown_appcontext
def close_connection(exception):
    pass


@app.errorhandler(500)
def page_not_found(e):

    aac().render('500.html', e=e)

@app.route('/')
@app.route('/index')
def index():

    return aac().renderer.render('index.html')


@app.route('/bundles.<ct>')
def bundle_index(ct):

    r = aac().renderer.cts(ct)

    cxt = dict(
        bundles=[b for b in r.library.bundles],
        **r.cc()
    )

    return r.render('toc/bundles.html', **cxt)

@app.route('/bundles/<vid>.<ct>')
def bundle_about(vid, ct):

    r = aac().renderer.cts(ct)

    cxt = dict(
        vid=vid,
        b=r.library.bundle(vid),
        sources_header=['name', 'source_table_name', 'ref'],
        **r.cc()
    )

    return r.render('bundle/about.html', **cxt)

@app.route('/bundles/<vid>/meta.<ct>')
def bundle_meta(vid, ct):

    r = aac().renderer.cts(ct)

    def flatten_dict(d):
        def expand(key, value):
            if isinstance(value, dict):
                return [(key + '.' + k, v) for k, v in flatten_dict(value).items()]
            else:
                return [(key, value)]

        items = [item for k, v in d.items() for item in expand(k, v)]

        return dict(items)

    b = r.library.bundle(vid)

    metadata = { k : sorted(flatten_dict(v).items()) for k, v in b.metadata.dict.items() }

    cxt = dict(
        vid=vid,
        b=b,
        metadata=sorted(metadata.items()),
        **r.cc()
    )

    return r.render('bundle/meta.html', **cxt)

@app.route('/bundles/<vid>/files.<ct>')
def bundle_files(vid, ct):

    r = aac().renderer.cts(ct)

    cxt = dict(
        vid=vid,
        b=r.library.bundle(vid),
        **r.cc()
    )

    return r.render('bundle/partitions.html', **cxt)

@app.route('/bundles/<vid>/documentation.<ct>')
def bundle_documentation(vid, ct):

    r = aac().renderer.cts(ct)

    cxt = dict(
        vid=vid,
        b=r.library.bundle(vid),
        **r.cc()

    )

    return r.render('bundle/documentation.html', **cxt)

@app.route('/bundles/<vid>/sources.<ct>')
def bundle_sources(vid, ct):
    from ambry.util import drop_empty

    r = aac().renderer.cts(ct)

    b = r.library.bundle(vid)

    sources = []
    for i, row in enumerate(b.sources):
        if not sources:
            sources.append(list(row.dict.keys()))

        sources.append(list(row.dict.values()))

    sources = drop_empty(sources)

    cxt = dict(
        vid=vid,
        b=b,
        sources = sources[1:] if sources else [],
        sources_header = ['name','source_table_name','ref'],
        **r.cc()

    )

    return r.render('bundle/sources.html', **cxt)

@app.route('/bundles/<vid>/build.<ct>')
def bundle_build(vid, ct):

    r = aac().renderer.cts(ct)

    cxt = dict(
        vid=vid,
        b=r.library.bundle(vid),
        **r.cc()

    )

    return r.render('bundle/build.html', **cxt)

@app.route('/bundles/<vid>/file/<name>')
def bundle_file(vid,name):
    """Return a file from the bundle"""
    from cStringIO import StringIO
    from ambry.orm.file import File

    m = { v:k for k,v in File.path_map.items()}

    b = aac().renderer.library.bundle(vid)

    bs = b.build_source_files.file(m[name])

    sio = StringIO()

    bs.record_to_fh(sio)

    return send_file(StringIO(sio.getvalue()))

    sio.close()

@app.route('/search/bundle')
def bundle_search():
    """Search for a datasets and partitions, using a structured JSON term."""

    return aac().renderer.bundle_search(terms=request.args['terms'])

@app.route('/bundles/<vid>/tables/<tvid>.<ct>')
def get_table(vid, tvid, ct):

    r = aac().renderer.cts(ct)
    b = r.library.bundle(vid)

    cxt = dict(
        vid=vid,
        tvid=tvid,
        b=b,
        t=b.table(tvid),
        **r.cc()

    )

    return r.render('bundle/table.html', **cxt)

@app.route('/bundles/<bvid>/partitions/<pvid>.<ct>')
def get_bundle_partitions(bvid, pvid, ct):
    r = aac().renderer.cts(ct)
    b = r.library.bundle(bvid)
    p = b.partition(pvid)

    # FIXME This should be cached somewhere.

    source_names = [ s.name for s in p.table.sources ]

    docs = []

    for k, v in b.metadata.external_documentation.group_by_source().items():
        if k in source_names:
            for d in v:
                docs += v

    cxt = dict(
        vid=bvid,
        b=b,
        p=p,
        t=p.table,
        docs=docs,
        **r.cc()

    )

    return r.render('bundle/partition.html', **cxt)

@app.route('/file/<pvid>.<ct>')
def stream_file(pvid,ct):
    from flask import Response
    import cStringIO as StringIO
    import unicodecsv as csv

    r = aac().renderer.cts(ct)
    p = r.library.partition(pvid)

    if p.is_local:
        reader = p.reader
    else:
        reader = p.remote_datafile.reader

    def yield_row(w, b, row):
        w.writerow(row)
        b.seek(0)
        data = b.read()
        b.seek(0)
        b.truncate()
        return data


    def stream():
        b = StringIO.StringIO()
        writer = csv.writer(b)

        yield yield_row(writer, b, reader.headers)

        for row in reader.rows:
            yield yield_row(writer, b, row)



    return Response(stream(), mimetype='text/csv')

#--------------------------
# Old Code Below Here


# Really should be  serving this from a static directory, but this
# is easier for now.
@app.route('/css/<name>')
def css_file(name):
    return send_from_directory(aac().renderer.css_dir, name)


@app.route('/js/<path:path>')
def js_file(path):
    import os.path

    return send_from_directory(*os.path.split(os.path.join(aac().renderer.js_dir,path)))



@app.route('/databases.<ct>')
def databases_ct(ct):
    return renderer(content_type=ct).databases()



@app.route('/search/place')
def place_search():
    """Search for a place, using a single term."""

    return renderer().place_search(term=request.args.get('term'))





@app.route('/bundles/summary/<vid>.<ct>')
def get_bundle_summary(vid, ct):
    return renderer(content_type=ct).bundle_summary(vid)


@app.route('/bundles/<vid>/schema.<ct>')
def get_schema(vid, ct):

    if ct == 'csv':
        return renderer().schemacsv(vid)
    else:
        return renderer(content_type=ct).schema(vid)



@app.route('/tables.<ct>')
def get_tables(ct):

    return renderer(content_type=ct).tables_index()








@app.route('/collections.<ct>')
def get_collections(ct):

    return renderer(content_type=ct).collections_index()


@app.route('/stores/<sid>.<ct>')
def get_store(sid, ct):

    return renderer(content_type=ct).store(sid)


@app.route('/stores/<sid>/tables/<tvid>.<ct>')
def get_store_table(sid, tvid, ct):

    return renderer(content_type=ct).store_table(sid, tvid)


@app.route('/sources.<ct>')
def get_sources(ct):

    return renderer(content_type=ct).sources()


@app.route('/warehouses/<wid>/extracts/<tid>.<ct>')
def get_extract(wid, tid, ct):
    """Return an extract for a table."""

    from os.path import basename, dirname
    from ambry.orm.exc import NotFoundError
    from flask import Response


    if ct == 'csv':

        row_gen = warehouse(wid).stream_table(tid, content_type=ct)

        return Response(row_gen(), mimetype='text/csv')

    else:

        try:

            path, attach_filename = warehouse(wid).extract_table(tid, content_type=ct)

            return send_from_directory(directory=dirname(path),
                                       filename=basename(path),
                                       as_attachment=True,
                                       attachment_filename=attach_filename)
        except NotFoundError:
            abort(404)


@app.route('/warehouses/<wid>/sample/<tid>')
def get_sample(wid, tid, ct):
    """Return an extract for a table."""

    # from os.path import basename, dirname
    from ambry.orm.exc import NotFoundError

    try:
        warehouse(wid).extract_table(tid, content_type='json')
        # path, attach_filename = warehouse(wid).extract_table(tid, content_type='json')

    except NotFoundError:
        abort(404)


@app.route('/warehouses/<wid>/extractors/<tid>')
def get_extractors(wid, tid):
    from ambry.warehouse.extractors import get_extractors

    return jsonify(results=get_extractors(warehouse(wid).orm_table(tid)))


@app.route('/warehouses/download/<wid>.db')
def get_download(wid):
    from os.path import basename, dirname
    w = warehouse(wid)
    path = w.database.path
    return send_from_directory(directory=dirname(path),
                               filename=basename(path),
                               as_attachment=True,
                               attachment_filename="{}.db".format(wid))


def warehouse(uid):
    return renderer().library.warehouse(uid)
