from ..payment import Payment

commands = ["/withdraw"]


def process_admin_messages(message):
    if message == "/withdraw":
        return {""}