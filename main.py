import webapp2
from webapp2_extras import routes

from application.config.constants import DOMAIN_ROUTE

# API V1 HANDLERS
from application.handlers.api.v1.newslists import NewsListsApiHandler
from application.handlers.error import ErrorHandler

# API ROUTES
api = webapp2.WSGIApplication([
    routes.DomainRoute(
        DOMAIN_ROUTE, [
            webapp2.Route('/api/v1/newslist', handler=NewsListsApiHandler),
        ])
], debug=True)

api.error_handlers[500] = ErrorHandler.log_exception
api.error_handlers[501] = ErrorHandler.log_exception
api.error_handlers[405] = ErrorHandler.not_implemented
api.error_handlers[404] = ErrorHandler.log_not_found
