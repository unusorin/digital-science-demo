from fastapi_sso.sso.google import GoogleSSO

google_sso = GoogleSSO(
    "478687203488-g5ks835jmlci1l6vfo4g1k7v3jft9ngv.apps.googleusercontent.com",
    "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",
    "http://localhost:8000/auth_callback",
    allow_insecure_http=True
)
