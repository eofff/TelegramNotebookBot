from updater import Updater
import time

updater_obj = Updater()

while True:
    updater_obj.update()
    time.sleep(5)