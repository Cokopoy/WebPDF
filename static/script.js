let currentFileId = null;
let currentPage = 1;
let totalPages = 1;
let filePreviewRotation = {};

// Load file list and folders on page load
document.addEventListener('DOMContentLoaded', function() {
    loadFolders();
    loadFileList();
    
    // File input handlers
    document.getElementById('pdfInput').addEventListener('change', function(e) {
        uploadFiles(e.target.files, 'pdf');
        this.value = '';
    });
    
    document.getElementById('imageInput').addEventListener('change', function(e) {
        uploadFiles(e.target.files, 'image');
        this.value = '';
    });
});

async function loadFolders() {
    try {
        const response = await fetch('/api/folders');
        const data = await response.json();
        
        document.getElementById('inputFolderDisplay').textContent = data.input_folder;
        document.getElementById('outputFolderDisplay').textContent = data.output_folder;
    } catch (error) {
        console.error('Error loading folders:', error);
    }
}

function openFolderModal() {
    document.getElementById('folderModal').classList.add('show');
    loadFolders();
}

function closeFolderModal() {
    document.getElementById('folderModal').classList.remove('show');
    loadFolders();
}

function toggleInputFolderInput() {
    const input = document.getElementById('inputFolderInput');
    const display = document.getElementById('inputFolderDisplay');
    
    if (input.style.display === 'none') {
        // Show input field and pre-fill with current folder
        input.value = display.textContent;
        input.style.display = 'block';
        input.focus();
        input.select();
    } else {
        // Hide input and save if not empty
        const folder = input.value.trim();
        if (folder) {
            setInputFolder(folder);
        }
        input.style.display = 'none';
    }
}

function toggleOutputFolderInput() {
    const input = document.getElementById('outputFolderInput');
    const display = document.getElementById('outputFolderDisplay');
    
    if (input.style.display === 'none') {
        // Show input field and pre-fill with current folder
        input.value = display.textContent;
        input.style.display = 'block';
        input.focus();
        input.select();
    } else {
        // Hide input and save if not empty
        const folder = input.value.trim();
        if (folder) {
            setOutputFolder(folder);
        }
        input.style.display = 'none';
    }
}

async function setInputFolder(folder) {
    try {
        const response = await fetch('/api/set-input-folder', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ folder: folder })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Folder input berhasil diubah', 'success');
            loadFolders();
        } else {
            showNotification('Error: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error setting input folder:', error);
        showNotification('Error mengubah folder', 'error');
    }
}

async function setOutputFolder(folder) {
    try {
        console.log('[DEBUG] Setting output folder to:', folder);
        const response = await fetch('/api/set-output-folder', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ folder: folder })
        });
        
        const data = await response.json();
        console.log('[DEBUG] Response:', data);
        
        if (data.success) {
            console.log('[+] Output folder set to:', data.folder);
            showNotification('Folder output berhasil diubah: ' + data.folder, 'success');
            loadFolders();
        } else {
            console.error('[!] Error:', data.error);
            showNotification('Error: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error setting output folder:', error);
        showNotification('Error mengubah folder', 'error');
    }
}

function showFolderDialog(type) {
    showNotification('Fitur browse folder akan datang. Gunakan paste path untuk sementara.', 'info');
}

async function loadFileList() {
    try {
        const response = await fetch('/api/files');
        const files = await response.json();
        
        const fileList = document.getElementById('fileList');
        
        if (files.length === 0) {
            fileList.innerHTML = '<p class="empty-message">Belum ada file yang ditambahkan</p>';
            return;
        }
        
        fileList.innerHTML = '';
        files.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                <span class="file-item-name" title="${file.name}">${file.name}</span>
                <span class="file-item-type">${file.type === 'pdf' ? 'PDF' : 'Gambar'}</span>
                <button class="file-item-delete" onclick="deleteFile(${index})">Hapus</button>
            `;
            
            fileItem.addEventListener('click', function(e) {
                if (!e.target.classList.contains('file-item-delete')) {
                    selectFile(index);
                }
            });
            
            fileList.appendChild(fileItem);
        });
    } catch (error) {
        console.error('Error loading files:', error);
    }
}

function selectFile(fileId) {
    currentFileId = fileId;
    currentPage = 1;
    
    // Update UI
    document.querySelectorAll('.file-item').forEach((item, index) => {
        item.classList.toggle('selected', index === fileId);
    });
    
    // Reset rotation transform before loading new preview
    const previewImage = document.getElementById('previewImage');
    if (filePreviewRotation[fileId]) {
        previewImage.style.transform = `rotate(${filePreviewRotation[fileId]}deg)`;
    } else {
        previewImage.style.transform = 'rotate(0deg)';
    }
    
    loadPreview(fileId);
}

async function loadPreview(fileId) {
    try {
        const response = await fetch(`/api/preview/${fileId}?page=${currentPage}`);
        const data = await response.json();
        
        const previewImage = document.getElementById('previewImage');
        const previewEmpty = document.getElementById('previewEmpty');
        const previewInfo = document.getElementById('previewInfo');
        const pageNav = document.getElementById('pageNav');
        
        if (data.error) {
            previewInfo.textContent = 'Error: ' + data.error;
            previewImage.style.display = 'none';
            previewEmpty.style.display = 'flex';
            pageNav.style.display = 'none';
            return;
        }
        
        // Display the preview image
        previewImage.src = data.image;
        previewImage.style.display = 'block';
        previewEmpty.style.display = 'none';
        
        if (data.type === 'pdf') {
            totalPages = data.total_pages;
            previewInfo.textContent = `File ${fileId + 1} - Halaman ${data.page} dari ${data.total_pages}`;
            pageNav.style.display = 'flex';
            document.getElementById('pageInfo').textContent = `Halaman ${data.page} dari ${data.total_pages}`;
        } else {
            previewInfo.textContent = `File ${fileId + 1} - Gambar (${data.width}x${data.height}px)`;
            pageNav.style.display = 'none';
        }
    } catch (error) {
        console.error('Error loading preview:', error);
        document.getElementById('previewInfo').textContent = 'Error loading preview: ' + error.message;
        document.getElementById('previewImage').style.display = 'none';
        document.getElementById('previewEmpty').style.display = 'flex';
    }
}

async function uploadFiles(fileList, type) {
    const formData = new FormData();
    
    for (let file of fileList) {
        formData.append('files', file);
    }
    
    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            loadFileList();
            showNotification(`${data.added.length} file berhasil ditambahkan`, 'success');
        } else {
            showNotification('Gagal mengunggah file: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error uploading files:', error);
        showNotification('Error mengunggah file', 'error');
    }
}

async function deleteFile(fileId) {
    if (!confirm('Hapus file ini?')) return;
    
    try {
        const response = await fetch(`/api/remove/${fileId}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            loadFileList();
            if (currentFileId === fileId) {
                currentFileId = null;
                document.getElementById('previewImage').src = '';
                document.getElementById('previewInfo').textContent = 'Pilih file untuk melihat preview';
            }
            showNotification('File berhasil dihapus', 'success');
        }
    } catch (error) {
        console.error('Error deleting file:', error);
        showNotification('Error menghapus file', 'error');
    }
}

async function clearAllFiles() {
    if (!confirm('Kosongkan semua file? Tindakan ini tidak dapat dibatalkan.')) return;
    
    try {
        const response = await fetch('/api/clear', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            loadFileList();
            currentFileId = null;
            document.getElementById('previewImage').src = '';
            document.getElementById('previewInfo').textContent = 'Pilih file untuk melihat preview';
            showNotification('Semua file berhasil dihapus', 'success');
        }
    } catch (error) {
        console.error('Error clearing files:', error);
        showNotification('Error menghapus file', 'error');
    }
}

async function moveFile(direction) {
    if (currentFileId === null) {
        showNotification('Pilih file terlebih dahulu', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/api/move', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                file_id: currentFileId,
                direction: direction
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            loadFileList();
            showNotification(`File dipindahkan ke ${direction === 'up' ? 'atas' : 'bawah'}`, 'success');
        }
    } catch (error) {
        console.error('Error moving file:', error);
        showNotification('Error memindahkan file', 'error');
    }
}

function previousPage() {
    if (currentPage > 1) {
        currentPage--;
        loadPreview(currentFileId);
    }
}

function nextPage() {
    if (currentPage < totalPages) {
        currentPage++;
        loadPreview(currentFileId);
    }
}

function rotatePreview(angle) {
    const image = document.getElementById('previewImage');
    if (!image.src) {
        showNotification('Pilih file terlebih dahulu', 'warning');
        return;
    }
    
    // Apply CSS rotation
    if (!filePreviewRotation[currentFileId]) {
        filePreviewRotation[currentFileId] = 0;
    }
    
    if (angle === 0) {
        filePreviewRotation[currentFileId] = 0;
    } else {
        filePreviewRotation[currentFileId] = (filePreviewRotation[currentFileId] + angle) % 360;
    }
    
    image.style.transform = `rotate(${filePreviewRotation[currentFileId]}deg)`;
    showNotification(`Preview diputar ${filePreviewRotation[currentFileId]}°`, 'info');
}

async function mergePDF() {
    // Get file list first
    const response = await fetch('/api/files');
    const files = await response.json();
    
    if (files.length === 0) {
        showNotification('Tambahkan minimal 1 file sebelum menggabung', 'warning');
        return;
    }
    
    showProgressModal(true);
    updateProgress(30, 'Mempersiapkan file...');
    
    try {
        setTimeout(() => {
            updateProgress(60, 'Menggabung file...');
        }, 500);
        
        // Prepare rotation data
        const rotations = {};
        for (let i = 0; i < files.length; i++) {
            rotations[i] = filePreviewRotation[i] || 0;
        }
        
        const mergeResponse = await fetch('/api/merge', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ rotations: rotations })
        });
        
        if (mergeResponse.ok) {
            const data = await mergeResponse.json();
            
            updateProgress(100, 'Selesai!');
            
            setTimeout(() => {
                showProgressModal(false);
                if (data.success) {
                    showNotification(`PDF berhasil digabung ke: ${data.filepath}`, 'success');
                    
                    // Ask to clear files
                    if (confirm('Hapus file-file yang sudah digabung?')) {
                        clearAllFiles();
                    }
                } else {
                    showNotification('Error: ' + data.error, 'error');
                }
            }, 1000);
        } else {
            throw new Error('Gagal menggabung PDF');
        }
    } catch (error) {
        console.error('Error merging PDF:', error);
        showProgressModal(false);
        showNotification('Error menggabung PDF: ' + error.message, 'error');
    }
}

function showProgressModal(show) {
    const modal = document.getElementById('progressModal');
    if (show) {
        modal.classList.add('show');
    } else {
        modal.classList.remove('show');
    }
}

function updateProgress(percent, text) {
    const fill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    
    fill.style.width = percent + '%';
    fill.textContent = percent + '%';
    progressText.textContent = text;
}

function showNotification(message, type = 'info') {
    // Simple notification (you can enhance this with a toast library later)
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#2ecc71' : type === 'error' ? '#e74c3c' : type === 'warning' ? '#f39c12' : '#3498db'};
        color: white;
        border-radius: 5px;
        z-index: 2000;
        animation: slideIn 0.3s ease;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
