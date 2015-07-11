Some searches using the rest API:

http://localhost:8080/api/paciente/.json?search=adriano
http://localhost:8080/api/atendimento/.json?status=C
http://localhost:8080/api/atendimento/.json?status=C&instancia_tratamento__data=2011-09-15
http://localhost:8080/api/atendimento/.json?status=C&instancia_tratamento__data=2011-09-15&instancia_tratamento__tratamento__id=5
http://localhost:8080/api/notificacao/.json?atendimento__instancia_tratamento__tratamento__id=1
http://localhost:8080/api/notificacao/.json?atendimento__instancia_tratamento__tratamento__id=1&search=gustavo

By default, searches will use case-insensitive partial matches. The search parameter may contain multiple search terms, which should be whitespace and/or comma separated. If multiple search terms are used then objects will be returned in the list only if all the provided terms are matched.

The search behavior may be restricted by prepending various characters to the search_fields.

'^' Starts-with search.
'=' Exact matches.
'@' Full-text search. (Currently only supported Django's MySQL backend.)
For example:

search_fields = ('=username', '=email')

The OrderingFilter class supports simple query parameter controlled ordering of results. By default, the query parameter is named 'ordering', but this may by overridden with the ORDERING_PARAM setting.

For example, to order users by username:

http://example.com/api/users?ordering=username
