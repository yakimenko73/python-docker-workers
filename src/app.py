import multiprocessing

import app
from app import db
from app.docker.worker import WorkersManager

if __name__ == '__main__':
    app = app.create()
    db.init(app.config['TESTING'])

    worker = WorkersManager()
    process = multiprocessing.Process(target=worker.start)
    process.start()

    app.run()
