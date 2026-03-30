import os
import requests
import csv

# Function to download an image from a given URL and save it with a specified filename
def download_image(url, folder, filename, errors_file):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for any request errors

        # Create the full path for saving the image
        file_path = os.path.join(folder, f"{filename}.jpg")
        errors_file_path = os.path.join(folder, f"{filename}.jpg")

        # Save the image
        with open(file_path, 'wb') as f:
            f.write(response.content)

        print(f"Downloaded: {filename}.jpg")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {url}. Error: {e}")
        errors_file.write(f"Failed to download {url}. Error: {e}")
        errors_file.flush()

# Main function to read the CSV file and download the images
def download_images_from_csv(file_path, errors_file, folder):
    # Ensure the folder exists
    os.makedirs(folder, exist_ok=True)

    # Open the CSV file and read each row (assuming two columns: number, URL)
    with open(file_path, 'r') as file:
        reader = csv.reader(file, delimiter=';')
        
        for row in reader:
            print(row)
            if len(row) != 2:
                print(f"Skipping invalid row: {row}")
                continue

            number = row[0]
            url = row[1]
            number = number.strip()  # Number for the filename
            url = url.strip()  # URL of the image

            if url:
                download_image(url, folder, number, errors_file)

# Example usage
csv_file_path = 'resized_links.txt'  # Path to the CSV file with numbers and URLs
err_file = 'erros_download_imagens.txt'
download_folder = 'imagens2'  # Folder to save the images

errors_file = open(err_file, 'w')

download_images_from_csv(csv_file_path, errors_file, download_folder)

