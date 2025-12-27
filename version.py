"""
Zzzuper PDF - Version Information
"""

VERSION = {
    'app_name': 'Zzzuper PDF',
    'version': '1.0.0',
    'edition': 'Web Based',
    'release_date': 'December 27, 2025',
    'status': 'Production Ready',
    'python_version': '3.8+',
    'flask_version': '2.3.3',
}

FEATURES = [
    'Upload PDF and Images',
    'File Preview',
    'File Reordering',
    'PDF Merging',
    'Barcode Detection',
    'Responsive Design',
    'REST API',
    'Session Management',
]

SUPPORTED_FORMATS = {
    'pdf': 'Adobe PDF',
    'jpg': 'JPEG Image',
    'jpeg': 'JPEG Image',
    'png': 'PNG Image',
}

TECHNOLOGIES = {
    'backend': ['Flask', 'PyPDF2', 'PyMuPDF', 'Pillow', 'ReportLab'],
    'frontend': ['HTML5', 'CSS3', 'Vanilla JavaScript'],
    'infrastructure': ['Python 3.13.5', 'Virtual Environment', 'Flask Dev Server'],
}

def print_version():
    """Print version information"""
    print(f"\n{'='*50}")
    print(f"  {VERSION['app_name']} v{VERSION['version']}")
    print(f"  {VERSION['edition']} Edition")
    print(f"  {VERSION['status']}")
    print(f"{'='*50}\n")
    
    print(f"Release Date: {VERSION['release_date']}")
    print(f"Python Required: {VERSION['python_version']}")
    print(f"Flask Version: {VERSION['flask_version']}\n")
    
    print("Available Features:")
    for feature in FEATURES:
        print(f"  ✓ {feature}")
    print()

if __name__ == '__main__':
    print_version()
