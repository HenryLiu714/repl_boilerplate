"""
Repository module for data persistence.
Provides abstract interface and implementations for in-memory and SQLite storage.
"""

import json
import sqlite3
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Any


class Repository(ABC):
    """Abstract base class for data repositories."""

    @abstractmethod
    def create_table(self, table_id: str) -> bool:
        """
        Create a new entity.

        Args:
            table_id: Unique identifier for the entity
            data: Entity data as dictionary

        Returns:
            True if created successfully, False otherwise
        """
        pass

    @abstractmethod
    def add_record(self, table_id: str, record_id: str, data: Dict[str, Any]) -> bool:
        """
        Add a record to an entity.

        Args:
            table_id: Identifier of the entity
            record_id: Unique identifier for the record
            data: Record data as dictionary

        Returns:
            True if added successfully, False otherwise
        """
        pass

    @abstractmethod
    def get_record(self, table_id: str, record_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a record from an entity.

        Args:
            table_id: Identifier of the entity
            record_id: Identifier of the record

        Returns:
            Record data as dictionary if found, None otherwise
        """
        pass

    @abstractmethod
    def list_records(self, table_id: str) -> List[Dict[str, Any]]:
        """
        List all records in an entity.

        Args:
            table_id: Identifier of the entity

        Returns:
            List of record data dictionaries
        """
        pass

    @abstractmethod
    def delete_record(self, table_id: str, record_id: str) -> bool:
        """
        Delete a record from an entity.

        Args:
            table_id: Identifier of the entity
            record_id: Identifier of the record

        Returns:
            True if deleted successfully, False otherwise
        """
        pass

    @abstractmethod
    def delete_table(self, table_id: str) -> bool:
        """
        Delete an entire entity.

        Args:
            table_id: Identifier of the entity

        Returns:
            True if deleted successfully, False otherwise
        """
        pass

class InMemoryRepository(Repository):
    """In-memory repository implementation."""

    def __init__(self):
        """Initialize the in-memory repository."""
        self.storage: Dict[str, Dict[str, Any]] = {}

    def create_table(self, table_id: str) -> bool:
        """Create a new entity."""
        if table_id in self.storage:
            return False  # Entity already exists
        self.storage[table_id] = {}
        return True

    def add_record(self, table_id: str, record_id: str, data: Dict[str, Any]) -> bool:
        """Add a record to an entity."""
        if table_id not in self.storage:
            return False  # Entity does not exist
        self.storage[table_id][record_id] = data
        return True

    def get_record(self, table_id: str, record_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a record from an entity."""
        if table_id not in self.storage:
            return None  # Entity does not exist

        if record_id not in self.storage[table_id]:
            return None  # Record does not exist

        return self.storage.get(table_id, {}).get(record_id)

    def list_records(self, table_id: str) -> List[Dict[str, Any]]:
        """List all records in an entity."""
        if table_id not in self.storage:
            return []  # Entity does not exist
        return list(self.storage[table_id].values())

    def delete_record(self, table_id: str, record_id: str) -> bool:
        """Delete a record from an entity."""
        if table_id not in self.storage:
            return False  # Entity does not exist

        if record_id not in self.storage[table_id]:
            return False  # Record does not exist

        del self.storage[table_id][record_id]
        return True

    def delete_table(self, table_id: str) -> bool:
        """Delete an entire entity."""
        if table_id not in self.storage:
            return False  # Entity does not exist
        del self.storage[table_id]
        return True