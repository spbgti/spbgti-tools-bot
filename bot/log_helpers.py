import logging

logger = logging.getLogger("telegramBot")


def log_with_args(func):
    def wrapper(*args):
        print("Entering function {0} ".format(func.__name__)
              + " with arguments: " + str(list(args)))
        res = func(*args)
        print("Exiting function {0} ".format(func.__name__)
              + " with return res: " + str(res))
        return res

    return wrapper
