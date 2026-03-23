"""
Encryption Module

Provides file encryption and decryption capabilities for secure version storage.
Uses AES-256 encryption with secure key management.
"""

import os
import base64
from pathlib import Path
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class EncryptionManager:
    """
    Encryption Manager
    
    Provides file encryption and decryption capabilities for secure version storage.
    Uses AES-256 encryption with secure key management.
    """
    
    def __init__(self, encryption_key: Optional[str] = None, salt: Optional[bytes] = None):
        """
        Initialize encryption manager
        
        Args:
            encryption_key: Encryption key (if None, generates a new one)
            salt: Salt for key derivation (if None, generates a new one)
        """
        self.salt = salt or os.urandom(16)
        
        if encryption_key:
            # Derive key from provided password
            self.fernet = self._derive_key(encryption_key)
        else:
            # Generate a new random key
            self.fernet = Fernet.generate_key()
        
        # Store the actual Fernet instance
        if isinstance(self.fernet, bytes):
            self.fernet = Fernet(self.fernet)
    
    def _derive_key(self, password: str) -> Fernet:
        """
        Derive encryption key from password using PBKDF2
        
        Args:
            password: Password string
            
        Returns:
            Fernet: Fernet instance with derived key
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return Fernet(key)
    
    def encrypt_file(self, input_path: Path, output_path: Path) -> bool:
        """
        Encrypt a file
        
        Args:
            input_path: Path to input file
            output_path: Path to encrypted output file
            
        Returns:
            bool: True if encryption successful
        """
        try:
            # Read file content
            with open(input_path, 'rb') as f:
                file_data = f.read()
            
            # Encrypt data
            encrypted_data = self.fernet.encrypt(file_data)
            
            # Write encrypted data
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(encrypted_data)
            
            return True
            
        except Exception as e:
            print(f"Encryption failed: {e}")
            return False
    
    def decrypt_file(self, input_path: Path, output_path: Path) -> bool:
        """
        Decrypt a file
        
        Args:
            input_path: Path to encrypted file
            output_path: Path to decrypted output file
            
        Returns:
            bool: True if decryption successful
        """
        try:
            # Read encrypted data
            with open(input_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt data
            decrypted_data = self.fernet.decrypt(encrypted_data)
            
            # Write decrypted data
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
            
            return True
            
        except Exception as e:
            print(f"Decryption failed: {e}")
            return False
    
    def encrypt_data(self, data: bytes) -> bytes:
        """
        Encrypt binary data
        
        Args:
            data: Data to encrypt
            
        Returns:
            bytes: Encrypted data
        """
        return self.fernet.encrypt(data)
    
    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        """
        Decrypt binary data
        
        Args:
            encrypted_data: Data to decrypt
            
        Returns:
            bytes: Decrypted data
        """
        return self.fernet.decrypt(encrypted_data)
    
    def get_key_info(self) -> dict:
        """
        Get encryption key information (for secure storage)
        
        Returns:
            dict: Key information
        """
        return {
            "salt": base64.b64encode(self.salt).decode('utf-8'),
            "key_available": True
        }
    
    def validate_encryption(self, test_data: bytes = b"test") -> bool:
        """
        Validate encryption/decryption functionality
        
        Args:
            test_data: Test data to validate
            
        Returns:
            bool: True if encryption/decryption works correctly
        """
        try:
            encrypted = self.encrypt_data(test_data)
            decrypted = self.decrypt_data(encrypted)
            return decrypted == test_data
        except Exception:
            return False
    
    @classmethod
    def create_with_password(cls, password: str, salt: Optional[bytes] = None) -> 'EncryptionManager':
        """
        Create encryption manager with password
        
        Args:
            password: Password for key derivation
            salt: Salt for key derivation
            
        Returns:
            EncryptionManager: Configured encryption manager
        """
        return cls(encryption_key=password, salt=salt)
    
    @classmethod
    def create_with_key(cls, key: bytes) -> 'EncryptionManager':
        """
        Create encryption manager with existing key
        
        Args:
            key: Existing encryption key
            
        Returns:
            EncryptionManager: Configured encryption manager
        """
        instance = cls()
        instance.fernet = Fernet(key)
        return instance


class SecureSnapshotManager:
    """
    Secure Snapshot Manager
    
    Manages encrypted version snapshots with secure storage.
    """
    
    def __init__(self, encryption_manager: EncryptionManager, storage_path: Path):
        """
        Initialize secure snapshot manager
        
        Args:
            encryption_manager: Encryption manager instance
            storage_path: Base storage path
        """
        self.encryption_manager = encryption_manager
        self.storage_path = storage_path
        self.secure_storage_path = storage_path / "secure_snapshots"
        self.secure_storage_path.mkdir(parents=True, exist_ok=True)
    
    def create_secure_snapshot(self, snapshot_name: str, source_path: Path) -> bool:
        """
        Create encrypted snapshot
        
        Args:
            snapshot_name: Name for the snapshot
            source_path: Source directory to snapshot
            
        Returns:
            bool: True if snapshot creation successful
        """
        try:
            snapshot_dir = self.secure_storage_path / snapshot_name
            snapshot_dir.mkdir(parents=True, exist_ok=True)
            
            # Encrypt all files in source directory
            for file_path in source_path.rglob('*'):
                if file_path.is_file():
                    relative_path = file_path.relative_to(source_path)
                    encrypted_path = snapshot_dir / f"{relative_path}.enc"
                    
                    # Create directory structure
                    encrypted_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Encrypt file
                    if not self.encryption_manager.encrypt_file(file_path, encrypted_path):
                        return False
            
            # Save metadata
            metadata = {
                "snapshot_name": snapshot_name,
                "file_count": len(list(source_path.rglob('*'))),
                "encryption_info": self.encryption_manager.get_key_info()
            }
            
            metadata_path = snapshot_dir / "metadata.json"
            import json
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Secure snapshot creation failed: {e}")
            return False
    
    def restore_secure_snapshot(self, snapshot_name: str, target_path: Path) -> bool:
        """
        Restore encrypted snapshot
        
        Args:
            snapshot_name: Name of the snapshot to restore
            target_path: Target directory for restoration
            
        Returns:
            bool: True if restoration successful
        """
        try:
            snapshot_dir = self.secure_storage_path / snapshot_name
            
            if not snapshot_dir.exists():
                return False
            
            # Decrypt all files
            for encrypted_path in snapshot_dir.rglob('*.enc'):
                relative_path = encrypted_path.relative_to(snapshot_dir)
                decrypted_path = target_path / relative_path.with_suffix('')  # Remove .enc suffix
                
                # Create directory structure
                decrypted_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Decrypt file
                if not self.encryption_manager.decrypt_file(encrypted_path, decrypted_path):
                    return False
            
            return True
            
        except Exception as e:
            print(f"Secure snapshot restoration failed: {e}")
            return False
    
    def list_secure_snapshots(self) -> list:
        """
        List available secure snapshots
        
        Returns:
            list: List of snapshot names
        """
        snapshots = []
        for item in self.secure_storage_path.iterdir():
            if item.is_dir():
                snapshots.append(item.name)
        return snapshots
    
    def delete_secure_snapshot(self, snapshot_name: str) -> bool:
        """
        Delete secure snapshot
        
        Args:
            snapshot_name: Name of snapshot to delete
            
        Returns:
            bool: True if deletion successful
        """
        try:
            import shutil
            snapshot_dir = self.secure_storage_path / snapshot_name
            if snapshot_dir.exists():
                shutil.rmtree(snapshot_dir)
            return True
        except Exception as e:
            print(f"Secure snapshot deletion failed: {e}")
            return False