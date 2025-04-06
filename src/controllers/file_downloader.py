from PySide6.QtCore import QObject, Signal, QUrl, QStandardPaths
from PySide6.QtWebEngineCore import QWebEngineDownloadRequest
from PySide6.QtWidgets import QMessageBox, QWidget
import os
import shutil
import tempfile

class FileDownloader(QObject):
    """A class to handle file downloads in the browser."""
    
    download_progress = Signal(str, int)  # filename, progress percentage
    download_finished = Signal(str, bool)  # filename, success
    download_error = Signal(str, str)  # filename, error message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_downloads = {}  # Keep track of active downloads
        self.temp_dir = os.path.join(tempfile.gettempdir(), "browser_downloads")
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def _get_unique_temp_path(self, base_path: str) -> str:
        """Generate a unique temporary path if the base path already exists."""
        if not os.path.exists(base_path):
            return base_path
            
        directory = os.path.dirname(base_path)
        filename = os.path.basename(base_path)
        name, ext = os.path.splitext(filename)
        
        counter = 1
        while True:
            temp_path = os.path.join(directory, f"{name} ({counter}){ext}")
            if not os.path.exists(temp_path):
                return temp_path
            counter += 1
    
    def start_download(self, download: QWebEngineDownloadRequest, save_path: str, dialog=None):
        """Start a new download."""
        try:
            # Get the suggested filename from the download request
            original_filename = download.suggestedFileName()
            if not original_filename:
                original_filename = os.path.basename(download.url().toString())
            
            # Get directory from save_path
            save_dir = os.path.dirname(save_path)
            user_filename = os.path.basename(save_path)
            
            # Determine the final filename:
            # 1. If user hasn't modified the name, use original_filename
            # 2. If user modified the name but kept extension, use user's name
            # 3. If user modified name and changed extension, warn and use original extension
            
            orig_name, orig_ext = os.path.splitext(original_filename)
            user_name, user_ext = os.path.splitext(user_filename)
            
            # If the user hasn't changed the filename or only added a number suffix
            if user_name == orig_name or user_name.startswith(orig_name + " ("):
                final_filename = original_filename
            else:
                # User changed the name - keep their name but ensure correct extension
                if not orig_ext:
                    # No original extension, use user's extension
                    final_filename = user_filename
                elif not user_ext:
                    # User removed extension, restore original
                    final_filename = user_name + orig_ext
                elif user_ext.lower() != orig_ext.lower():
                    # User changed extension - keep original for safety
                    final_filename = user_name + orig_ext
                    # Optionally notify about extension mismatch
                    if dialog:
                        dialog.show_warning(f"File extension changed to match original type: {orig_ext}")
                else:
                    # User kept the correct extension
                    final_filename = user_filename
            
            # Create temporary path
            temp_base_path = os.path.join(self.temp_dir, final_filename)
            temp_path = self._get_unique_temp_path(temp_base_path)
            temp_filename = os.path.basename(temp_path)
            
            # Update the final save path with the correct filename
            save_path = os.path.join(save_dir, final_filename)
            
            # Ensure the final download directory exists
            try:
                os.makedirs(save_dir, exist_ok=True)
                if not os.access(save_dir, os.W_OK):
                    raise PermissionError(f"No write permission for directory: {save_dir}")
            except Exception as e:
                raise Exception(f"Failed to create/access download directory: {str(e)}")
            
            # Check if final file exists and is writable
            if os.path.exists(save_path):
                if not os.access(save_path, os.W_OK):
                    raise PermissionError(f"Cannot write to existing file: {save_path}")
            
            # Store download info
            download_id = download.id()
            self.active_downloads[download_id] = {
                'request': download,
                'filename': final_filename,
                'temp_path': temp_path,
                'final_path': save_path,
                'total_bytes': download.totalBytes(),
                'received_bytes': 0,
                'dialog': dialog,
                'state': 'starting'
            }
            
            # Set download path to temporary location
            download.setDownloadDirectory(self.temp_dir)
            download.setDownloadFileName(temp_filename)
            
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
            error_msg = f"Failed to start download: {str(e)}"
            self.download_error.emit(
                os.path.basename(save_path),
                error_msg
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
                download_info['state'] = 'downloading'
                
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
                try:
                    # Move file from temp to final location
                    temp_path = download_info['temp_path']
                    final_path = download_info['final_path']
                    
                    if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                        # Move the file to its final location
                        shutil.move(temp_path, final_path)
                        download_info['state'] = 'completed'
                        self.download_finished.emit(filename, True)
                        if dialog:
                            dialog.accept()
                    else:
                        raise Exception("Downloaded file is empty or missing")
                        
                except Exception as e:
                    error_msg = f"Failed to save download: {str(e)}"
                    self.download_error.emit(filename, error_msg)
                    if dialog:
                        dialog.close()
                finally:
                    self._cleanup_download(download_id)
                
            elif state == QWebEngineDownloadRequest.DownloadState.DownloadCancelled:
                download_info['state'] = 'cancelled'
                self.download_finished.emit(filename, False)
                if dialog:
                    dialog.close()
                self._cleanup_download(download_id)
                
            elif state == QWebEngineDownloadRequest.DownloadState.DownloadInterrupted:
                download = download_info['request']
                error = download.interruptReason()
                error_msg = f"Download failed: {error}"
                download_info['state'] = 'failed'
                self.download_error.emit(filename, error_msg)
                if dialog:
                    dialog.close()
                self._cleanup_download(download_id)
                
        except Exception as e:
            if download_info:
                error_msg = f"Error handling state change: {str(e)}"
                self.download_error.emit(
                    download_info['filename'],
                    error_msg
                )
                if download_info.get('dialog'):
                    download_info['dialog'].close()
            self._cleanup_download(download_id)
    
    def _cleanup_download(self, download_id):
        """Clean up download resources."""
        try:
            if download_id in self.active_downloads:
                download_info = self.active_downloads[download_id]
                
                # Remove temporary file if it exists
                temp_path = download_info.get('temp_path')
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except:
                        pass  # Ignore cleanup errors
                
                del self.active_downloads[download_id]
        except:
            pass  # Ensure cleanup doesn't raise errors
    
    def cancel_download(self, download_id):
        """Cancel a specific download."""
        if download_id in self.active_downloads:
            download_info = self.active_downloads[download_id]
            download_info['state'] = 'cancelling'
            download_info['request'].cancel()
            if download_info.get('dialog'):
                download_info['dialog'].close()
    
    def cancel_all_downloads(self):
        """Cancel all active downloads."""
        for download_id, info in list(self.active_downloads.items()):
            info['state'] = 'cancelling'
            info['request'].cancel()
            if info.get('dialog'):
                info['dialog'].close()
    
    def __del__(self):
        """Clean up temporary directory on object destruction."""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass  # Ignore cleanup errors 