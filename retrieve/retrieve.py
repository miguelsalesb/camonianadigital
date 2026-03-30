import ssl
import urllib.request
import xml.etree.ElementTree as ET

class RetrieveData:
    NAMESPACE = {'unimarc': 'info:lc/xmlns/marcxchange-v2'}
    BASE_URL = "https://urn.bnportugal.gov.pt/ncb/unimarc/marcxchange?id="

    def __init__(self):
        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE

    def fetch(self, record_id: str) -> ET.Element | None:
        """Fetch and parse a UNIMARC/MarcXchange record by ID."""
        url = f"{self.BASE_URL}{record_id}"
        try:
            with urllib.request.urlopen(url, context=self.ctx) as response:
                raw = response.read()
            return ET.fromstring(raw)
        except urllib.error.HTTPError as e:
            print(f"HTTP error fetching '{record_id}': {e.code} {e.reason}")
        except urllib.error.URLError as e:
            print(f"URL error fetching '{record_id}': {e.reason}")
        except ET.ParseError as e:
            print(f"Failed to parse XML for '{record_id}': {e}")
        return None
        