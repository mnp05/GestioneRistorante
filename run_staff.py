import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

if __name__ == "__main__":
    from staff.main import StaffAppController
    controller = StaffAppController()
    controller.start()
