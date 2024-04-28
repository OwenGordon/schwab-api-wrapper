import sys
from .schwab import SchwabAPI


def main():
    print("Renewing OAuth token...")

    if len(sys.argv) < 2:
        print(
            "Insufficient arguments, please include a file path to parameters json file"
        )

    parameters_file_path = sys.argv[1]

    api = SchwabAPI(
        parameters_file_path, renew_refresh_token=True, immediate_refresh=False
    )
    api.renew_refresh_token()

    print(
        f"API OAuth Refresh Token has been renewed and written to {parameters_file_path}"
    )


if __name__ == "__main__":
    main()
