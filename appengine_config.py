from application.libraries.gaesessions import SessionMiddleware
from google.appengine.ext import vendor

vendor.add("application/libraries")

appstats_CALC_RPC_COSTS = True


def webapp_add_wsgi_middleware(app):
    from google.appengine.ext.appstats import recording
    app = recording.appstats_wsgi_middleware(app)
    app = SessionMiddleware(
        app,
        cookie_key=(
            "9GueYkdpw2FvAXcZNeqG31tPHU53kbgCL4xqjNMJmYcBMcrCsvA2Q12xOftGS4Hic"
            "1TDkpZHbQKM2DB220BhF7wCMF3BVKylHz3L0ZJJPJa9oFRpC8euMKfT0gY1PiMYi3"
            "mVi4k73lsDVLymeA4Q3JlJLaMjXnp4SaViHDmUBqVSSGuXAy1V14TWS0cjaawknqw"
            "pSwPX5a4AjkIdXGBVnXnTW4Y2C1OF3EgVnROBD7MFp4lIwM1J2J5k8gDkCsqIFP8d"
            "YMVfUp8vuscWqTecyMzks7efZl7vOCuhxg2iFdgd2YDlszLNjhLGaHvh4aYfcU7Oa"
            "4bAYOn2EKcAOdyTVrMrZk2igoATGQS2dVgTlkTUMUWRhBSK4aWqzV4Ba3YvfNIs6c"
            "WvyXfWS9FjpM8vplcQsys1"
        )
    )
    return app
