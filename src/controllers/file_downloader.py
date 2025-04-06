from PySide6.QtCore import QObject, Signal, QUrl, QStandardPaths
from PySide6.QtWebEngineCore import QWebEngineDownloadRequest, QWebEngineProfile
from PySide6.QtWidgets import QMessageBox, QWidget
from PySide6.QtNetwork import QNetworkReply
import os
import shutil
import tempfile
import time
import mimetypes

class FileDownloader(QObject):
    """A class to handle file downloads in the browser."""
    
    download_progress = Signal(str, int)  # filename, progress percentage
    download_finished = Signal(str, bool)  # filename, success
    download_error = Signal(str, str)  # filename, error message
    
    # Common video formats and their extensions
    VIDEO_FORMATS = {
        'video/mp4': '.mp4',
        'video/webm': '.webm',
        'video/ogg': '.ogv',
        'video/quicktime': '.mov',
        'video/x-matroska': '.mkv',
        'video/x-msvideo': '.avi',
        'video/x-flv': '.flv',
        'video/3gpp': '.3gp',
        'video/mpeg': '.mpeg'
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_downloads = {}  # Keep track of active downloads
        self.temp_dir = os.path.join(tempfile.gettempdir(), "browser_downloads")
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Configure retry settings
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        
        # Initialize mime types
        mimetypes.init()
    
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
    
    def _get_file_extension(self, download: QWebEngineDownloadRequest) -> str:
        """Determine the correct file extension based on MIME type and URL."""
        # Try to get MIME type from the download
        mime_type = download.mimeType().lower()
        
        # Check if it's a video format
        if mime_type in self.VIDEO_FORMATS:
            return self.VIDEO_FORMATS[mime_type]
            
        # Try to get extension from the URL
        url = download.url().toString()
        url_ext = os.path.splitext(url)[1].lower()
        if url_ext and len(url_ext) < 6:  # Reasonable extension length
            if url_ext in [ext for ext in self.VIDEO_FORMATS.values()]:
                return url_ext
        
        # Try to get extension from mime type
        if mime_type:
            ext = mimetypes.guess_extension(mime_type)
            if ext:
                return ext
        
        # Default to mp4 for video types without clear extension
        if mime_type.startswith('video/'):
            return '.mp4'
            
        # Return empty if no extension could be determined
        return ''
    
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
            
            # Determine the final filename
            orig_name, orig_ext = os.path.splitext(original_filename)
            user_name, user_ext = os.path.splitext(user_filename)
            
            # For video files, ensure we have the correct extension
            if download.mimeType().startswith('video/'):
                correct_ext = self._get_file_extension(download)
                if correct_ext:
                    if not user_ext or user_ext.lower() != correct_ext.lower():
                        user_ext = correct_ext
                        if dialog:
                            dialog.show_warning(f"File extension changed to match video format: {correct_ext}")
            
            # If the user hasn't changed the filename or only added a number suffix
            if user_name == orig_name or user_name.startswith(orig_name + " ("):
                final_filename = original_filename
            else:
                # User changed the name - keep their name but ensure correct extension
                if not orig_ext and user_ext:
                    # No original extension, use user's extension
                    final_filename = user_filename
                elif not user_ext and orig_ext:
                    # User removed extension, restore original
                    final_filename = user_name + orig_ext
                elif orig_ext and user_ext and user_ext.lower() != orig_ext.lower():
                    # User changed extension - for videos, use detected extension
                    if download.mimeType().startswith('video/'):
                        final_filename = user_name + (correct_ext if correct_ext else orig_ext)
                    else:
                        final_filename = user_name + orig_ext
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
            
            # Configure download settings
            download.setDownloadDirectory(self.temp_dir)
            download.setDownloadFileName(temp_filename)
            
            # For video downloads, don't use HTML save format
            if not download.mimeType().startswith('video/'):
                download.setSavePageFormat(QWebEngineDownloadRequest.CompleteHtmlSaveFormat)
            
            # Store download info with retry count
            download_id = download.id()
            self.active_downloads[download_id] = {
                'request': download,
                'filename': final_filename,
                'temp_path': temp_path,
                'final_path': save_path,
                'total_bytes': download.totalBytes(),
                'received_bytes': 0,
                'dialog': dialog,
                'state': 'starting',
                'retry_count': 0,
                'last_progress_time': time.time(),
                'is_video': download.mimeType().startswith('video/')
            }
            
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
            current_time = time.time()
            
            # Check for stalled download
            if received > 0 and received == download_info['received_bytes']:
                time_since_last_progress = current_time - download_info['last_progress_time']
                if time_since_last_progress > 30:  # 30 seconds timeout
                    self._retry_download(download_id)
                    return
            
            if total > 0:
                progress = int((received / total) * 100)
                self.download_progress.emit(download_info['filename'], progress)
                download_info['received_bytes'] = received
                download_info['total_bytes'] = total
                download_info['state'] = 'downloading'
                download_info['last_progress_time'] = current_time
                
                # Update dialog if it exists
                if download_info['dialog']:
                    download_info['dialog'].update_progress(progress)
                
        except Exception as e:
            filename = download_info['filename'] if download_info else 'Unknown'
            self.download_error.emit(
                filename,
                f"Error updating progress: {str(e)}"
            )
    
    def _retry_download(self, download_id: int):
        """Retry a failed download."""
        try:
            download_info = self.active_downloads.get(download_id)
            if not download_info:
                return
            
            if download_info['retry_count'] >= self.max_retries:
                error_msg = "Download failed after maximum retries"
                self.download_error.emit(download_info['filename'], error_msg)
                if download_info['dialog']:
                    download_info['dialog'].close()
                self._cleanup_download(download_id)
                return
            
            # Increment retry count
            download_info['retry_count'] += 1
            
            # Cancel current download
            download_info['request'].cancel()
            
            # Wait before retrying
            time.sleep(self.retry_delay)
            
            # Get the original URL and create a new download
            original_url = download_info['request'].url()
            
            # Get the default profile
            profile = QWebEngineProfile.defaultProfile()
            
            # Connect to downloadRequested signal temporarily to catch the new download
            def handle_new_download(new_download):
                profile.downloadRequested.disconnect(handle_new_download)
                self.start_download(
                    new_download,
                    download_info['final_path'],
                    download_info['dialog']
                )
            
            profile.downloadRequested.connect(handle_new_download)
            
            # Trigger a new download by navigating to the URL
            # This will be caught by our temporary handler above
            profile.download(original_url)
            
        except Exception as e:
            if download_info:
                error_msg = f"Error retrying download: {str(e)}"
                self.download_error.emit(download_info['filename'], error_msg)
                if download_info['dialog']:
                    download_info['dialog'].close()
            self._cleanup_download(download_id)
    
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
                
                # Check if we should retry
                if download_info['retry_count'] < self.max_retries:
                    self._retry_download(download_id)
                else:
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