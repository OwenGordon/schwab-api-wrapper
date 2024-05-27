import sys
from .schwab import SchwabAPI
import json


def usage():
    print("Usage: python3 -m schwab-api-wrapper <parameters filepath> [-r | -n]\n\n\t-r: restart OAuth2 and renew refresh token\n\t-n: generate a new parameters json with all necessary fields")


def main():
    if len(sys.argv) < 3:
        print(
            "Insufficient arguments, please include a file path to parameters json file and mode\n"
        )
        usage()
        exit(1)

    parameters_file_path = sys.argv[1]
    mode = sys.argv[2]

    if mode == "-r":
        print("Renewing OAuth token...")

        api = SchwabAPI(
            parameters_file_path, renew_refresh_token=True, immediate_refresh=False
        )
        api.renew_refresh_token()

        print(
            f"API OAuth Refresh Token has been renewed and written to {parameters_file_path}"
        )
    
    elif mode == "-n":
        print("Generating new parameters json")

        empty_parameters = {
            "client_id": "App Key here",
            "client_secret": "Secret here",
            "redirect_uri": "Callback URL here",
            "expires_in": 0,
            "token_type": "",
            "scope": "",
            "refresh_token": "",
            "access_token": "",
            "id_token": "",
            "access_token_valid_until": "",
            "refresh_token_valid_until": ""
        }

        with open(parameters_file_path, "w") as fin:
            json.dump(empty_parameters, fin, indent=4)
        
        print(f"New parameters json file created at {parameters_file_path}")

    else:
        print(f"Unknown mode: {mode}")
        usage()
        exit(1)


if __name__ == "__main__":
    main()
