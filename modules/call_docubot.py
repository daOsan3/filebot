import requests

def call_docubot(input_dir, output_dir):
    base_url = "http://docubot:8020/docubot"  # Use 'docubot' as hostname
    params = {
        "input_dir": input_dir,
        "output_dir": output_dir,
    }
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        print("API call was successful.")
        print("Response:", response.json())
    else:
        print(f"API call failed. Status code: {response.status_code}")
        print("Response:", response.text)

if __name__ == "__main__":
    input_dir = "/app/filebot-store-000/chrome-extension"
    output_dir = "/app/filebot-store-000/chrome-extension"
    call_docubot(input_dir, output_dir)
