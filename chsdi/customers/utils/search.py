from collections import namedtuple


SearchKeywords = namedtuple('SearchKeywords', 'keywords filter_keys')


SEARCH_KEYWORDS = (
    # address, rank 20
    SearchKeywords(
        keywords=('addresse', 'adresse', 'indirizzo', 'address'),
        filter_keys=['communes', 'sorted_buildings']),
)
