from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search as es_Search

from django.conf import settings

from .mailroom import parse_query

ES = Elasticsearch(hosts=[settings.ELASTICSEARCH_URL])


def query_contact_ids(org, query, *, group=None, return_parsed_query=False):
    """
    Returns the contact ids for the given query
    """
    parsed = parse_query(org, query, group=group)
    results = (
        es_Search(index="contacts").source(include=["id"]).params(routing=org.id).using(ES).query(parsed.elastic_query)
    )

    # In case if you also need to return parsed query (e.g. to display it to users)
    # you just need to pass `return_parsed_query` in kwargs as `True`
    if return_parsed_query:
        return [int(r.id) for r in results.scan()], parsed.query

    return [int(r.id) for r in results.scan()]


def get_last_modified():
    """
    Gets the last modified contact if there are any contacts
    """
    results = (
        es_Search(index="contacts")
        .params(size=1)
        .sort("-modified_on_mu")
        .source(include=["modified_on", "id"])
        .using(ES)
        .execute()
    )
    hits = results["hits"]["hits"]
    return hits[0]["_source"] if hits else None
