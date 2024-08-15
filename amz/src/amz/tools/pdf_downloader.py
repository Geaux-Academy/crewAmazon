from typing import List, Dict
import aiohttp
import asyncio
import os
import logging
from tqdm import tqdm
import fitz  # PyMuPDF

class PDFDownloader:
    def __init__(self, download_dir: str = "downloads", retries: int = 3, backoff_factor: float = 0.3, headers: dict = None):
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)

        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }

        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler()]
        )

    async def download_pdf(self, session: aiohttp.ClientSession, url: str, timeout: int = 10) -> str:
        """
        Download a PDF file from a given URL and save it to the download directory.
        """
        try:
            logging.info(f"Starting download from {url}")
            async with session.get(url, headers=self.headers, timeout=timeout) as response:
                response.raise_for_status()  # Check if the request was successful

                # Check if the response content is PDF
                if 'application/pdf' not in response.headers.get('Content-Type', ''):
                    raise ValueError("The URL does not point to a PDF file")

                # Extract the file name from the URL
                filename = os.path.join(self.download_dir, url.split("/")[-1])

                # Write the content to a file
                with open(filename, 'wb') as file:
                    file.write(await response.read())

                logging.info(f"Successfully downloaded {filename}")
                return filename
        except aiohttp.ClientError as e:
            logging.error(f"Failed to download {url}. Error: {str(e)}")
            return f"Failed to download {url}. Error: {str(e)}"
        except ValueError as ve:
            logging.error(f"Invalid content from URL {url}. Error: {str(ve)}")
            return f"Invalid content from URL {url}. Error: {str(ve)}"
        except Exception as ex:
            logging.error(f"An unexpected error occurred. Error: {str(ex)}")
            return f"An unexpected error occurred. Error: {str(ex)}"

    async def download_pdfs(self, urls: List[str]) -> List[str]:
        """
        Download multiple PDFs from a list of URLs.
        """
        async with aiohttp.ClientSession() as session:
            tasks = [self.download_pdf(session, url) for url in urls]
            results = []
            for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Downloading PDFs"):
                result = await f
                results.append(result)
            return results

    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text from a PDF file using PyMuPDF.
        """
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        except Exception as e:
            logging.error(f"Failed to extract text from {file_path}. Error: {str(e)}")
            return f"Failed to extract text from {file_path}. Error: {str(e)}"

    def extract_metadata_from_pdf(self, file_path: str) -> Dict[str, str]:
        """
        Extract metadata from a PDF file using PyMuPDF.
        """
        try:
            doc = fitz.open(file_path)
            metadata = doc.metadata
            return metadata
        except Exception as e:
            logging.error(f"Failed to extract metadata from {file_path}. Error: {str(e)}")
            return {"error": str(e)}

# Testing the updated PDFDownloader class
if __name__ == "__main__":
    urls = [
        "https://www.cs.cmu.edu/~pattis/15-1XX/15-200/lectures/python.pdf",
        "https://www.csc.kth.se/utbildning/kth/kurser/DD1310/jupyter/Python.pdf"
        # Add other URLs
    ]
    downloader = PDFDownloader()
    loop = asyncio.get_event_loop()
    download_results = loop.run_until_complete(downloader.download_pdfs(urls))
    for result in download_results:
        if not result.startswith("Failed"):
            text = downloader.extract_text_from_pdf(result)
            metadata = downloader.extract_metadata_from_pdf(result)
            print(f"Text from {result}:\n{text[:500]}...")  # Print first 500 characters of text
            print(f"Metadata from {result}:\n{metadata}")
        else:
            print(result)
