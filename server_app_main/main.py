import os
from app import create_app, db
from flask_migrate import Migrate
from app.db_utils import *
from app.models import *


app = create_app('development')
migrate = Migrate(app, db)


if __name__ == '__main__':
    with app.app_context():
        # task_model_utils = TaskModelUtils()
        # task_model_utils.wait_for_finish_printing_of_task(1, 300)
        db.drop_all()
        db.create_all()
        gen_a_lot_of_printers()
        # task_model_utils = TaskModelUtils()
        # task_history_model_utils = TaskHistoryModelUtils()
        # file_model_utils = FileModelUtils()
        # user_model_utils = UserModelUtils()
        # task_model_utils.add_new_task(1, 1, 5, 100, [file_model_utils.get_all_user_files(1)[0]])
        #
        ...

    app.run()
