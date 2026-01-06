import os
import time
import tarfile
import requests
import xml.etree.ElementTree as ET
from urllib.request import urlretrieve
from tqdm import tqdm

def get_arxiv_ids(category="cs.CL", max_results=1000):
    """
    Fetch arXiv IDs for a given category using arXiv API.
    """
    base_url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": f"cat:{category}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }
    
    print(f"Fetching {max_results} papers from {category}...")
    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        print("Error fetching arXiv data")
        return []
        
    root = ET.fromstring(response.content)
    # Namespace is usually http://www.w3.org/2005/Atom
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    
    ids = []
    for entry in root.findall('atom:entry', ns):
        id_url = entry.find('atom:id', ns).text
        # ID format: http://arxiv.org/abs/2101.00001 -> 2101.00001
        paper_id = id_url.split('/')[-1]
        ids.append(paper_id)
        
    return ids

def download_source(paper_id, save_dir):
    """
    Download source tarball for a paper ID.
    Returns True if successful.
    """
    url = f"https://arxiv.org/e-print/{paper_id}"
    save_path = os.path.join(save_dir, f"{paper_id}.tar.gz")
    extract_path = os.path.join(save_dir, paper_id)
    
    if os.path.exists(extract_path):
        # Already downloaded and extracted
        return True
        
    try:
        # User-Agent is required by arXiv
        headers = {'User-Agent': 'LFM-CiteAgent/0.1.0 (mailto:gyunggyung@example.com)'}
        response = requests.get(url, headers=headers, stream=True)
        
        if response.status_code != 200:
            # print(f"Failed to download {paper_id}: Status {response.status_code}")
            return False
            
        # Check content type - sometimes it redirects to PDF if source not available
        content_type = response.headers.get('content-type', '')
        if 'application/pdf' in content_type:
             # print(f"Source not available for {paper_id} (PDF only)")
             return False
             
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        # Extract
        try:
            if tarfile.is_tarfile(save_path):
                with tarfile.open(save_path) as tar:
                    tar.extractall(path=extract_path)
            else:
                # Sometimes it's a single file (not typical for recent papers but possible)
                # print(f"Not a tar file: {paper_id}")
                return False
        except Exception as e:
            # print(f"Error extracting {paper_id}: {e}")
            return False
            
        # Cleanup tar
        os.remove(save_path)
        return True
        
    except Exception as e:
        print(f"Error processing {paper_id}: {e}")
        if os.path.exists(save_path):
            os.remove(save_path)
        return False

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", type=str, default="cs.CL")
    parser.add_argument("--count", type=int, default=200) # Increased for data volume
    parser.add_argument("--data_dir", type=str, default="./data/arxiv_source")
    args = parser.parse_args()
    
    os.makedirs(args.data_dir, exist_ok=True)
    
    # 1. Get IDs
    ids = get_arxiv_ids(args.category, args.count)
    print(f"Found {len(ids)} papers. Starting download...")
    
    # 2. Download
    success_count = 0
    for pid in tqdm(ids):
        if download_source(pid, args.data_dir):
            success_count += 1
        time.sleep(3) # Respect arXiv rate limits (important!)
        
    print(f"Successfully downloaded {success_count} sources.")

if __name__ == "__main__":
    main()
