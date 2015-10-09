from osc2mqtt import main

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv[1:]) or 0)
