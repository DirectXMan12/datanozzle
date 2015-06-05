Python Datagrepper Client
=========================

This library acts as a wrapper around the wonderful
[requests](https://python-requests.org) library for accessing
[Datagrepper](https://apps.fedoraproject.org/datagrepper/).

Requirements
------------

- Python 3.3+
- [requests](https://python-requests.org)

Usage
-----

The API is designed around being chainable.  To start, create a new `Grepper`:

    >>> from datagrepper.client import Grepper
    >>> g = Grepper()
    >>>

Then, you can build up queries by chaining methods (each new method returns a new
query object, so you can reuse partially built queries):

    >>> q1 = g.by_user('sross').ascending
    >>> q2 = q1.by_topic('org.fedoraproject.prod.fedbadges.person.rank.advance')
    >>>

Queries are not executed until they are evaluated by iterating over them (the library will
automatically continue to fetch new pages of information).  Each record is returned as an `Entry`,
which has several persistent fields (which are accessible as properties), and additional data
available in a dict-like manner:

    >>> entry = next(iter(q2.take(pages=1)))
    >>> entry.topic
    'org.fedoraproject.prod.fedbadges.person.rank.advance'
    >>> entry.timestamp
    datetime.datetime(2015, 1, 16, 15, 2, 5)
    >>> entry['person']['nickname']
    'sross'
    >>>

Most queries can support multiple values.  You can either pass multiple values, like
`g.by_user('sross', 'someuser')` or chain, like `g.by_user('sross').by_user('someuser')`. 
To get a query with a parameter reset, call `reset(parameter_name)`, like `g.reset('user')`.


Queries
-------

- `by_user(*users)`: filter by FAS username
- `without_user(*users)`: inverse of `by_user`
- `by_package(*packages)`: filter by package name
- `without_package(*packages)`: inverse of `by_package`
- `by_category(*categories)`: filter by category (the third or fourth part of the topic)
- `without_category(*categories)`: inverse of `by_category`
- `by_topic(*topics)`: filter by topic
- `without_topic(*topics)`: inverse of `by_topic`
- `containing(substring)`: filter by keyword in the message
- `paginate(rows)`: set the number of rows per page
- `with_meta(*meta_type)`: return additional meta-information with the results
- `grouped` (*property*): group similar results together
- `ascending` (*property*): sort results in ascending order
- `descending` (*property*): sort results in descending order
- `take(pages)`: only return results from the first *pages* pages
- `skip(pages)`: skip the first *pages* pages
- `starting_at(start)`: return results from after the given date/time
- `ending_at(end)`: return results from before the given date/time
- `delta_seconds(delta)`: modify start/end times by *delta* seconds

Data Properties
---------------

- `certificate`: a string containing the certificate
- `signature`: a string containing the signature
- `meta`: a dict containing additional meta-information
- `index`: the message index
- `timestamp`: a `datetime` containing the timestamp for the object
- `topic`: the topic of the message
