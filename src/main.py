from tidal_wrapper import TidalWrapper

def main():
    auth = TidalWrapper()
    auth.setup_account()

if __name__ == "__main__":
    main()