def filter_country(events, country):

    return [
        event
        for event in events
        if event.country.lower() == country.lower()
    ]


def filter_severity(events, severity):

    return [
        event
        for event in events
        if event.severity.lower() == severity.lower()
    ]


def filter_source(events, source):

    return [
        event
        for event in events
        if event.source.lower() == source.lower()
    ]
