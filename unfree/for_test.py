from lib import *

class Random_state(I):
    category = 'browser'
    def install(self): pass
    def remove(self): pass
    def installed(self):
        import random
        v = random.randint(0, 1)
        return bool(v)

class Insane(I):
    category = 'browser'
    def install(self):
        pass
    def remove(self):
        pass
    def installed(self):
        return False

class Command_fail(I):
    category = 'browser'
    def install(self):
        raise CommandFailError('command')
    def remove(self):
        pass
    def installed(self):
        return False

class Download_fail(I):
    category = 'browser'
    def install(self):
        raise CannotDownloadError('url')
    def remove(self):
        pass
    def installed(self):
        return False

class Long_sleep(I):
    category = 'browser'
    def install(self):
        run('sleep 100')
    def remove(self):
        pass
    def installed(self):
        return False

class Installed_raise_exception(I):
    category = 'browser'
    x = 0
    def install(self):
        pass
    def remove(self):
        pass
    def installed(self):
        self.x += 1
        if self.x > 1: raise Exception
        else: return False