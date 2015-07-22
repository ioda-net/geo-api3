from sqlalchemy.sql.expression import cast
from sqlalchemy import Text, or_


def full_text_search(query, ormColumns, searchText):
    ''' Given a list of columns and a searchText, returns
    a filtered query '''
    def ilike_search(col):
        if col is not None:
            return cast(col, Text).ilike('%%%s%%' % searchText)
    return query.filter(or_(
        *map(ilike_search, ormColumns)
    ))
