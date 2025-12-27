import os
import io
import time
import datetime
import json
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session, send_file, url_for
from werkzeug.utils import secure_filename
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from PIL import Image
import fitz
from pdf2image import convert_from_path

app = Flask(__name__)
app.secret_key = 'zuperpdf-secret-key-2024'

# Configuration
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
CONFIG_FILE = os.path.join(os.getcwd(), '.zuperpdf_config.json')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

def load_config():
    """Load configuration from file"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_config(config):
    """Save configuration to file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"[!] Error saving config: {e}")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_list_from_session():
    """Get file list from session"""
    if 'file_list' not in session:
        session['file_list'] = []
        session['file_types'] = []
        session['preview_rotations'] = {}
        session['page_orientations'] = {}
        
        # Load folders from config file, not session
        config = load_config()
        session['input_folder'] = config.get('input_folder', str(Path.home() / 'Documents'))
        session['output_folder'] = config.get('output_folder', str(Path.home() / 'Downloads'))
    return session.get('file_list', []), session.get('file_types', [])

def save_file_list_to_session(file_list, file_types):
    """Save file list to session"""
    session['file_list'] = file_list
    session['file_types'] = file_types
    session.modified = True

def get_barcode_from_first_file():
    """Extract barcode from first file"""
    try:
        from pyzbar.pyzbar import decode
        file_list, file_types = get_file_list_from_session()
        
        if not file_list:
            return None
        
        file_path = file_list[0]
        file_type = file_types[0]
        
        try:
            if file_type == "pdf":
                images = convert_from_path(file_path, first_page=1, last_page=1, dpi=200)
                if images:
                    decoded = decode(images[0])
                    if decoded:
                        return decoded[0].data.decode('utf-8').replace("X", "")
            else:
                img = Image.open(file_path)
                decoded = decode(img)
                if decoded:
                    return decoded[0].data.decode('utf-8').replace("X", "")
        except Exception as e:
            print(f"Error reading barcode: {e}")
            return None
        
        return None
    except ImportError:
        return None

@app.route('/')
def index():
    file_list, file_types = get_file_list_from_session()
    return render_template('index.html', file_count=len(file_list))

@app.route('/api/files', methods=['GET'])
def get_files():
    file_list, file_types = get_file_list_from_session()
    files = []
    for i, (f, ftype) in enumerate(zip(file_list, file_types)):
        files.append({
            'id': i,
            'name': os.path.basename(f),
            'path': f,
            'type': ftype
        })
    return jsonify(files)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    file_list, file_types = get_file_list_from_session()
    
    added = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = int(time.time() * 1000)
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Determine file type
            ext = filename.rsplit('.', 1)[1].lower()
            if ext == 'pdf':
                ftype = 'pdf'
            else:
                ftype = 'image'
            
            file_list.append(filepath)
            file_types.append(ftype)
            added.append({'name': os.path.basename(filename), 'type': ftype})
    
    save_file_list_to_session(file_list, file_types)
    
    return jsonify({
        'success': True,
        'added': added,
        'total': len(file_list)
    })

@app.route('/api/preview/<int:file_id>', methods=['GET'])
def preview_file(file_id):
    file_list, file_types = get_file_list_from_session()
    
    if file_id < 0 or file_id >= len(file_list):
        return jsonify({'error': 'Invalid file ID'}), 400
    
    file_path = file_list[file_id]
    file_type = file_types[file_id]
    page = request.args.get('page', 1, type=int)
    
    try:
        if file_type == 'pdf':
            doc = fitz.open(file_path)
            total_pages = doc.page_count
            
            if page < 1:
                page = 1
            if page > total_pages:
                page = total_pages
            
            page_obj = doc.load_page(page - 1)
            
            # Get page dimensions to determine orientation
            page_rect = page_obj.get_rect()
            page_w = page_rect.width
            page_h = page_rect.height
            is_landscape = page_w > page_h
            
            # Render at 2x zoom (same as merge)
            pix = page_obj.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Store original rendered dimensions
            original_width = img.width
            original_height = img.height
            
            # Resize for web display
            max_width = 600
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.LANCZOS)
            
            img_io = io.BytesIO()
            img.save(img_io, 'JPEG', quality=75)
            img_io.seek(0)
            import base64
            img_base64 = base64.b64encode(img_io.getvalue()).decode()
            
            return jsonify({
                'type': 'pdf',
                'page': page,
                'total_pages': total_pages,
                'image': f"data:image/jpeg;base64,{img_base64}",
                'original_width': original_width,
                'original_height': original_height,
                'is_landscape': is_landscape
            })
        else:
            img = Image.open(file_path).convert('RGB')
            
            # Get original dimensions
            original_width = img.width
            original_height = img.height
            is_landscape = original_width > original_height
            
            # Resize for web
            max_width = 600
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.LANCZOS)
            
            img_io = io.BytesIO()
            img.save(img_io, 'JPEG', quality=75)
            img_io.seek(0)
            import base64
            img_base64 = base64.b64encode(img_io.getvalue()).decode()
            
            return jsonify({
                'type': 'image',
                'width': img.width,
                'height': img.height,
                'image': f"data:image/jpeg;base64,{img_base64}",
                'original_width': original_width,
                'original_height': original_height,
                'is_landscape': is_landscape
            })
    except Exception as e:
        print(f"Preview error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/remove/<int:file_id>', methods=['POST'])
def remove_file(file_id):
    file_list, file_types = get_file_list_from_session()
    
    if file_id < 0 or file_id >= len(file_list):
        return jsonify({'error': 'Invalid file ID'}), 400
    
    try:
        filepath = file_list[file_id]
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"Error removing file: {e}")
    
    file_list.pop(file_id)
    file_types.pop(file_id)
    save_file_list_to_session(file_list, file_types)
    
    return jsonify({'success': True})

@app.route('/api/clear', methods=['POST'])
def clear_files():
    file_list, file_types = get_file_list_from_session()
    
    # Delete all uploaded files
    for filepath in file_list:
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            print(f"Error removing file: {e}")
    
    session['file_list'] = []
    session['file_types'] = []
    session['preview_rotations'] = {}
    session.modified = True
    
    return jsonify({'success': True})

@app.route('/api/move', methods=['POST'])
def move_file():
    data = request.get_json()
    file_id = data.get('file_id')
    direction = data.get('direction')
    
    file_list, file_types = get_file_list_from_session()
    
    if file_id < 0 or file_id >= len(file_list):
        return jsonify({'error': 'Invalid file ID'}), 400
    
    if direction == 'up' and file_id > 0:
        file_list[file_id], file_list[file_id - 1] = file_list[file_id - 1], file_list[file_id]
        file_types[file_id], file_types[file_id - 1] = file_types[file_id - 1], file_types[file_id]
    elif direction == 'down' and file_id < len(file_list) - 1:
        file_list[file_id], file_list[file_id + 1] = file_list[file_id + 1], file_list[file_id]
        file_types[file_id], file_types[file_id + 1] = file_types[file_id + 1], file_types[file_id]
    
    save_file_list_to_session(file_list, file_types)
    
    return jsonify({'success': True})

@app.route('/api/merge', methods=['POST'])
def merge_pdf():
    file_list, file_types = get_file_list_from_session()
    
    if not file_list:
        return jsonify({'error': 'No files to merge'}), 400
    
    # Get rotation data from request
    data = request.get_json() or {}
    rotations = data.get('rotations', {})
    
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.utils import ImageReader
        
        temp_pdf = io.BytesIO()
        c = canvas.Canvas(temp_pdf, pageCompression=1)
        
        for idx, (file_path, file_type) in enumerate(zip(file_list, file_types)):
            rotation = int(rotations.get(str(idx), 0))
            if file_type == "pdf":
                try:
                    doc = fitz.open(file_path)
                    for page_num in range(doc.page_count):
                        page = doc.load_page(page_num)
                        
                        # Get page dimensions to determine orientation
                        page_rect = page.get_rect()
                        page_w = page_rect.width
                        page_h = page_rect.height
                        is_landscape = page_w > page_h
                        
                        # Render at 2x zoom (same as preview)
                        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        
                        # Apply rotation if specified (negate for correct direction)
                        if rotation != 0:
                            img = img.rotate(-rotation, expand=True, fillcolor='white')
                        
                        img_w, img_h = img.size
                        
                        # After rotation, re-determine if landscape or portrait
                        is_landscape = img_w > img_h
                        
                        # Create custom page size matching aspect ratio
                        if is_landscape:
                            page_width = 11 * 72  # 11 inches in points
                            page_height = page_width * img_h / img_w
                        else:
                            page_height = 11 * 72  # 11 inches in points  
                            page_width = page_height * img_w / img_h
                        
                        c.setPageSize((page_width, page_height))
                        
                        # Convert image to buffer
                        img_buf = io.BytesIO()
                        img.save(img_buf, format='JPEG', quality=85)
                        img_buf.seek(0)
                        
                        # Draw image at full size
                        c.drawImage(ImageReader(img_buf), 0, 0, width=page_width, height=page_height)
                        c.showPage()
                finally:
                    try:
                        doc.close()
                    except:
                        pass
            else:
                # Handle image files
                img = Image.open(file_path).convert('RGB')
                
                # Apply rotation if specified (negate for correct direction)
                if rotation != 0:
                    img = img.rotate(-rotation, expand=True, fillcolor='white')
                
                img_w, img_h = img.size
                is_landscape = img_w > img_h
                
                # Create custom page size matching aspect ratio
                if is_landscape:
                    page_width = 11 * 72  # 11 inches in points
                    page_height = page_width * img_h / img_w
                else:
                    page_height = 11 * 72  # 11 inches in points
                    page_width = page_height * img_w / img_h
                
                c.setPageSize((page_width, page_height))
                
                # Convert image to buffer
                img_buf = io.BytesIO()
                img.save(img_buf, format='JPEG', quality=85)
                img_buf.seek(0)
                
                # Draw image at full size
                c.drawImage(ImageReader(img_buf), 0, 0, width=page_width, height=page_height)
                c.showPage()
        
        c.save()
        temp_pdf.seek(0)
        
        reader = PdfReader(temp_pdf)
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        
        output_pdf = io.BytesIO()
        writer.write(output_pdf)
        output_pdf.seek(0)
        
        # Get barcode for filename
        barcode = get_barcode_from_first_file()
        if barcode:
            filename = f"{barcode}.pdf"
        else:
            filename = datetime.datetime.now().strftime("Scan_%Y%m%d_%H%M%S.pdf")
        
        # Get output folder from config file (most reliable source)
        config = load_config()
        output_folder = config.get('output_folder', session.get('output_folder', str(Path.home() / 'Downloads')))
        
        print(f"[DEBUG] Output folder loaded: {output_folder}")
        
        output_path = None
        try:
            # Verify folder exists and is writable
            os.makedirs(output_folder, exist_ok=True)
            
            # Test write access
            test_file = os.path.join(output_folder, '.write_test')
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                print(f"[+] Output folder is writable: {output_folder}")
            except Exception as e:
                print(f"[!] WARNING: Output folder may not be writable: {e}")
                print(f"[!] Falling back to Downloads folder")
                output_folder = str(Path.home() / 'Downloads')
            
            output_path = os.path.join(output_folder, filename)
            
            # Write to file
            output_pdf.seek(0)
            with open(output_path, 'wb') as f:
                f.write(output_pdf.read())
            print(f"[+] File saved to: {output_path}")
            
            # Delete original files from INPUT FOLDER after successful merge
            delete_results = {'success': [], 'failed': []}
            input_folder = session.get('input_folder')
            
            try:
                for file_path in file_list:
                    try:
                        # Extract original filename from uploaded file (remove timestamp prefix)
                        # Format: 1766779828478_591.jpg -> 591.jpg
                        uploaded_filename = os.path.basename(file_path)
                        
                        # Split by first underscore to remove timestamp
                        parts = uploaded_filename.split('_', 1)
                        if len(parts) == 2:
                            original_filename = parts[1]
                        else:
                            original_filename = uploaded_filename
                        
                        # Try to find and delete file in INPUT FOLDER
                        if input_folder and os.path.isdir(input_folder):
                            original_file_path = os.path.join(input_folder, original_filename)
                            
                            if os.path.exists(original_file_path):
                                os.remove(original_file_path)
                                print(f"[+] Deleted: {original_filename}")
                                delete_results['success'].append(original_filename)
                            else:
                                print(f"[!] Original file not found in input folder: {original_file_path}")
                                delete_results['failed'].append({'file': original_filename, 'reason': 'Not found in input folder'})
                        else:
                            print(f"[!] Input folder not set or invalid: {input_folder}")
                            delete_results['failed'].append({'file': original_filename, 'reason': 'Input folder not available'})
                    except Exception as e:
                        print(f"[!] Error deleting {uploaded_filename}: {str(e)}")
                        delete_results['failed'].append({'file': uploaded_filename, 'reason': str(e)})
                
                if delete_results['failed']:
                    print(f"[!] Delete summary - Success: {len(delete_results['success'])}, Failed: {len(delete_results['failed'])}")
                    for failed in delete_results['failed']:
                        print(f"    - {failed['file']}: {failed['reason']}")
                else:
                    print(f"[+] All original files deleted successfully!")
            except Exception as e:
                print(f"[!] Critical error in delete loop: {e}")
            
        except Exception as e:
            print(f"[!] Error saving to output folder: {e}")
            # Fallback to Downloads
            try:
                fallback_folder = str(Path.home() / 'Downloads')
                os.makedirs(fallback_folder, exist_ok=True)
                fallback_path = os.path.join(fallback_folder, filename)
                output_pdf.seek(0)
                with open(fallback_path, 'wb') as f:
                    f.write(output_pdf.read())
                output_path = fallback_path
                print(f"[!] Fallback: File saved to: {fallback_path}")
            except Exception as e2:
                print(f"[!] Critical error - could not save file: {e2}")
        
        # Return success response with file info
        if output_path and os.path.exists(output_path):
            return jsonify({
                'success': True,
                'message': 'File saved successfully',
                'filename': filename,
                'filepath': output_path
            })
        else:
            return jsonify({'error': 'Failed to save PDF file'}), 500
    
    except Exception as e:
        print(f"[!] Merge error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/rotate', methods=['POST'])
def rotate_page():
    data = request.get_json()
    file_id = data.get('file_id')
    angle = data.get('angle', 90)
    
    if 'preview_rotations' not in session:
        session['preview_rotations'] = {}
    
    session['preview_rotations'][str(file_id)] = angle
    session.modified = True
    
    return jsonify({'success': True})

@app.route('/api/folders', methods=['GET'])
def get_folders():
    """Get current input and output folders"""
    input_folder = session.get('input_folder', str(Path.home() / 'Documents'))
    output_folder = session.get('output_folder', str(Path.home() / 'Downloads'))
    
    return jsonify({
        'input_folder': input_folder,
        'output_folder': output_folder,
        'input_name': os.path.basename(input_folder) or input_folder,
        'output_name': os.path.basename(output_folder) or output_folder
    })

@app.route('/api/set-input-folder', methods=['POST'])
def set_input_folder():
    """Set input folder path"""
    data = request.get_json()
    folder = data.get('folder', '').strip()
    
    if not folder:
        return jsonify({'error': 'Invalid folder path'}), 400
    
    try:
        # Normalize path
        normalized_folder = str(Path(folder).expanduser().absolute())
        
        # Verify it's a directory
        if not os.path.isdir(normalized_folder):
            return jsonify({'error': 'Path is not a directory'}), 400
        
        # Store in session
        session['input_folder'] = normalized_folder
        session.modified = True
        
        # ALSO save to config file for persistence
        config = load_config()
        config['input_folder'] = normalized_folder
        save_config(config)
        
        print(f"[+] Input folder set to: {normalized_folder}")
        print(f"[+] Saved to config file")
        
        return jsonify({
            'success': True, 
            'folder': normalized_folder,
            'name': os.path.basename(normalized_folder) or normalized_folder
        })
    except Exception as e:
        print(f"[!] Error setting input folder: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/set-output-folder', methods=['POST'])
def set_output_folder():
    """Set output folder path"""
    data = request.get_json()
    folder = data.get('folder', '').strip()
    
    if not folder:
        return jsonify({'error': 'Invalid folder path'}), 400
    
    try:
        # Normalize path - handle both Windows and Unix paths
        normalized_folder = str(Path(folder).expanduser().absolute())
        
        # Create folder if it doesn't exist
        os.makedirs(normalized_folder, exist_ok=True)
        
        # Verify it's actually a directory
        if not os.path.isdir(normalized_folder):
            return jsonify({'error': 'Path is not a directory'}), 400
        
        # Store in session
        session['output_folder'] = normalized_folder
        session.modified = True
        
        # ALSO save to config file for persistence
        config = load_config()
        config['output_folder'] = normalized_folder
        save_config(config)
        
        print(f"[+] Output folder set to: {normalized_folder}")
        print(f"[+] Saved to config file")
        
        return jsonify({
            'success': True, 
            'folder': normalized_folder,
            'name': os.path.basename(normalized_folder) or normalized_folder
        })
    except Exception as e:
        print(f"[!] Error setting output folder: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/output-files', methods=['GET'])
def get_output_files():
    """Get list of PDF files in output folder"""
    try:
        config = load_config()
        output_folder = config.get('output_folder', session.get('output_folder', str(Path.home() / 'Downloads')))
        
        if not os.path.isdir(output_folder):
            return jsonify({'files': []})
        
        files = []
        for filename in os.listdir(output_folder):
            if filename.lower().endswith('.pdf'):
                filepath = os.path.join(output_folder, filename)
                file_size = os.path.getsize(filepath)
                file_time = os.path.getmtime(filepath)
                
                files.append({
                    'name': filename,
                    'size': file_size,
                    'size_mb': round(file_size / (1024*1024), 2),
                    'time': file_time,
                    'time_str': datetime.datetime.fromtimestamp(file_time).strftime('%Y-%m-%d %H:%M:%S')
                })
        
        # Sort by time (newest first)
        files.sort(key=lambda x: x['time'], reverse=True)
        
        return jsonify({'files': files, 'folder': output_folder})
    except Exception as e:
        print(f"[!] Error getting output files: {e}")
        return jsonify({'error': str(e), 'files': []}), 500

@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """Download PDF file from output folder"""
    try:
        # Sanitize filename to prevent path traversal
        safe_filename = secure_filename(filename)
        
        config = load_config()
        output_folder = config.get('output_folder', session.get('output_folder', str(Path.home() / 'Downloads')))
        
        filepath = os.path.join(output_folder, safe_filename)
        
        # Verify file exists and is in output folder
        if not os.path.exists(filepath) or not os.path.isfile(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        # Verify file is PDF
        if not safe_filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Invalid file type'}), 400
        
        return send_file(filepath, as_attachment=True, download_name=safe_filename)
    except Exception as e:
        print(f"[!] Error downloading file: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
