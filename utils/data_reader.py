"""
Data reader utilities for loading test data from various formats
"""
import json
import yaml
import csv
import os
from typing import Dict, List, Any
from utils.logger import Logger

logger = Logger.get_logger(__name__)


class DataReader:
    """Utility class for reading test data from external files"""
    
    @staticmethod
    def read_json(file_path: str) -> Dict[str, Any]:
        """
        Read data from JSON file
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Dictionary containing the JSON data
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                logger.info(f"Successfully loaded JSON data from {file_path}")
                return data
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from {file_path}: {e}")
            raise
    
    @staticmethod
    def read_yaml(file_path: str) -> Dict[str, Any]:
        """
        Read data from YAML file
        
        Args:
            file_path: Path to YAML file
            
        Returns:
            Dictionary containing the YAML data
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
                logger.info(f"Successfully loaded YAML data from {file_path}")
                return data
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML from {file_path}: {e}")
            raise
    
    @staticmethod
    def read_csv(file_path: str) -> List[Dict[str, Any]]:
        """
        Read data from CSV file
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            List of dictionaries containing the CSV data
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                data = list(reader)
                logger.info(f"Successfully loaded CSV data from {file_path}")
                return data
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except csv.Error as e:
            logger.error(f"Error reading CSV from {file_path}: {e}")
            raise
