import runtimeConfig

cdef str hello():
    return u'Hello, world!'

app = runtimeConfig.app

@app.route("/")
def index():
    return hello()
