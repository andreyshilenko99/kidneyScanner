import multiprocessing

from settings import get_args, Config


def launch_core():
    from app.core import core
    loop = core()
    loop.run_forever()


def main():
    args = get_args()
    _config = Config(path=args.config)
    multiprocessing.set_start_method(_config['M_START_METHOD'], force=True)
    launch_core()


if __name__ == '__main__':
    main()
