# facebook-images-downloader
 A tool to download all the images of a [Facebook](https://www.facebook.com) page.

# Getting Started

Requires:
- Python 3, which you can download [here](https://www.python.org/downloads/), along with the *selenium* library;
- [geckodriver](https://github.com/mozilla/geckodriver), a Firefox WebDriver (refer to its repository for installation instructions).

Download the file *facebook-downloader.py* from this repository.

# Usage

Open the command prompt from the folder where *facebook-downloader.py* is located and run the following command:

````
python facebook-downloader.py [URL]
````

replacing [URL] with the URL of the Facebook page of which you want to download the images.

If you want to download images in different folders based on the albums they are located in, you can pass this argument:

````
-a, --album         download images in different folders corresponding to the albums they are located in
````

The script will create a *facebook* folder, a subfolder with the name of the page, and eventually a subfolder for each album where the images will be saved.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/giovanni-cutri/facebook-images-downloader/blob/main/LICENSE) file for details.
