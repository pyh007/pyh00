


dsn = 'http://3916478e508249d7b729123b45065147:7f95cb535a8947d7ac43c1df85ce7a8f@118.24.29.15 :9000/5'

DSN = "http://631512fc8908467f857ccf314732c014:1e2bc868e812468d882ac830875dc660@118.24.29.15 :9000/7"


from raven import Client

client = Client(DSN)

try:
    1 / 0
except ZeroDivisionError:
    client.captureException()