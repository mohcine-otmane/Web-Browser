from PySide6.QtCore import QObject, Signal, QUrl
from PySide6.QtWebEngineCore import QWebEngineDownloadRequest
from PySide6.QtWidgets import QMessageBox
import os

class FileDownloader(QObject):
    """A class to handle file downloads in the browser."""
    
    download_progress = Signal(str, int)  # filename, progress percentage
    download_finished = Signal(str, bool)  # filename, success
    download_error = Signal(str, str)  # filename, error message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_downloads = {}  # Keep track of active downloads
        
    def start_download(self, download: QWebEngineDownloadRequest, save_path: str, dialog=None):
        """Start a new download."""
        try:
            # Ensure the download directory exists
            download_dir = os.path.dirname(save_path)
            os.makedirs(download_dir, exist_ok=True)
            
            # Store download info
            download_id = download.id()
            self.active_downloads[download_id] = {
                'request': download,
                'filename': os.path.basename(save_path),
                'total_bytes': download.totalBytes(),
                'received_bytes': 0,
                'dialog': dialog  # Store dialog reference
            }
            
            # Set download path
            download.setDownloadDirectory(download_dir)
            download.setDownloadFileName(os.path.basename(save_path))
            
            # Connect signals
            download.receivedBytesChanged.connect(
                lambda: self._update_progress(download_id)
            )
            download.stateChanged.connect(
                lambda state: self._handle_state_change(download_id, state)
            )
            
            # Start download
            download.accept()
            
        except Exception as e:
            self.download_error.emit(
                os.path.basename(save_path),
                f"Failed to start download: {str(e)}"
            )
            if download:
                download.cancel()
            if dialog:
                dialog.close()
    
    def _update_progress(self, download_id: int):
        """Update download progress."""
        try:
            download_info = self.active_downloads.get(download_id)
            if not download_info:
                return
            
            download = download_info['request']
            received = download.receivedBytes()
            total = download.totalBytes()
            
            if total > 0:
                progress = int((received / total) * 100)
                self.download_progress.emit(download_info['filename'], progress)
                download_info['received_bytes'] = received
                download_info['total_bytes'] = total
                
                # Update dialog if it exists
                if download_info['dialog']:
                    download_info['dialog'].update_progress(progress)
                
        except Exception as e:
            filename = download_info['filename'] if download_info else 'Unknown'
            self.download_error.emit(
                filename,
                f"Error updating progress: {str(e)}"
            )
    
    def _handle_state_change(self, download_id: int, state):
        """Handle download state changes."""
        try:
            download_info = self.active_downloads.get(download_id)
            if not download_info:
                return
                
            filename = download_info['filename']
            dialog = download_info['dialog']
            
            if state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
                self.download_finished.emit(filename, True)
                if dialog:
                    dialog.accept()
                self._cleanup_download(download_id)
                
            elif state == QWebEngineDownloadRequest.DownloadState.DownloadCancelled:
                self.download_finished.emit(filename, False)
                if dialog:
                    dialog.close()
                self._cleanup_download(download_id)
                
            elif state == QWebEngineDownloadRequest.DownloadState.DownloadInterrupted:
                download = download_info['request']
                error = download.interruptReason()
                error_msg = f"Download failed: {error}"
                self.download_error.emit(filename, error_msg)
                if dialog:
                    dialog.close()
                self._cleanup_download(download_id)
                
        except Exception as e:
            if download_info:
                self.download_error.emit(
                    download_info['filename'],
                    f"Error handling state change: {str(e)}"
                )
                if download_info.get('dialog'):
                    download_info['dialog'].close()
            self._cleanup_download(download_id)
    
    def _cleanup_download(self, download_id):
        """Remove download from active downloads."""
        if download_id in self.active_downloads:
            del self.active_downloads[download_id]
    
    def cancel_download(self, download_id):
        """Cancel a specific download."""
        if download_id in self.active_downloads:
            download_info = self.active_downloads[download_id]
            download_info['request'].cancel()
            if download_info.get('dialog'):
                download_info['dialog'].close()
    
    def cancel_all_downloads(self):
        """Cancel all active downloads."""
        for download_info in self.active_downloads.values():
            download_info['request'].cancel()
            if download_info.get('dialog'):
                download_info['dialog'].close()
        self.active_downloads.clear() 