if __name__ == '__main__':
    import sys
    from osc2mqtt import main

    sys.exit(main(sys.argv[1:]) or 0)
