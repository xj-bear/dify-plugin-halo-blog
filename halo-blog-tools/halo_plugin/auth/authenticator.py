"""
Halo authentication handler.
"""

import logging
from typing import Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..exceptions import AuthenticationError, APIError

logger = logging.getLogger(__name__)


class HaloAuthenticator:
    """Handles authentication with Halo CMS."""
    
    def __init__(self, base_url: str, timeout: int = 30):
        """
        Initialize authenticator.
        
        Args:
            base_url: Halo CMS base URL
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self._setup_session()
    
    def _setup_session(self) -> None:
        """Setup HTTP session with retry strategy."""
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Dify-Halo-Plugin/1.0'
        })
    
    def authenticate(self, token: str) -> Dict[str, Any]:
        """
        Authenticate with personal access token.
        
        Args:
            token: Personal access token
            
        Returns:
            Authentication info if successful
            
        Raises:
            AuthenticationError: If authentication fails
            APIError: If API request fails
        """
        if not token or not token.strip():
            raise AuthenticationError("Personal access token is required")
        
        # Set authorization header
        self.session.headers.update({
            'Authorization': f'Bearer {token}'
        })
        
        try:
            # Test authentication by trying to access posts endpoint (correct Halo API path)
            response = self.session.get(
                f"{self.base_url}/apis/content.halo.run/v1alpha1/posts?page=0&size=1",
                timeout=self.timeout
            )
            
            if response.status_code == 401:
                raise AuthenticationError("Invalid personal access token")
            elif response.status_code == 403:
                # Check if it's an insufficient scope error
                www_auth = response.headers.get('www-authenticate', '')
                if 'insufficient_scope' in www_auth.lower():
                    raise AuthenticationError("Insufficient permissions. Please ensure your token has at least 'post:manage' and 'moment:manage' permissions")
                else:
                    raise AuthenticationError("Insufficient permissions")
            elif response.status_code not in [200, 404]:
                raise APIError(
                    f"Authentication failed: HTTP {response.status_code}",
                    response.status_code
                )
            
            # Authentication successful, get basic info
            auth_info = {
                "authenticated": True,
                "base_url": self.base_url,
                "token_valid": True
            }
            
            # Try to get some basic system information
            try:
                posts_data = response.json()
                auth_info["posts_total"] = posts_data.get("total", 0)
                
                # Try to get categories and moments info
                categories_response = self.session.get(
                    f"{self.base_url}/apis/content.halo.run/v1alpha1/categories?page=0&size=1",
                    timeout=self.timeout
                )
                if categories_response.status_code == 200:
                    categories_data = categories_response.json()
                    auth_info["categories_total"] = categories_data.get("total", 0)
                
                moments_response = self.session.get(
                    f"{self.base_url}/apis/moment.halo.run/v1alpha1/moments?page=0&size=1",
                    timeout=self.timeout
                )
                if moments_response.status_code == 200:
                    moments_data = moments_response.json()
                    auth_info["moments_total"] = moments_data.get("total", 0)
                    
            except Exception as e:
                logger.warning(f"Failed to get system info: {e}")
            
            logger.info("Successfully authenticated with Halo CMS")
            return auth_info
            
        except requests.exceptions.Timeout:
            raise APIError("Authentication request timed out")
        except requests.exceptions.ConnectionError:
            raise APIError("Cannot connect to Halo CMS server")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Authentication request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {e}")
            raise AuthenticationError(f"Authentication failed: {str(e)}")
    
    def validate_permissions(self, required_permissions: list) -> bool:
        """
        Validate if current token has required permissions.
        
        Args:
            required_permissions: List of required permissions
            
        Returns:
            True if all permissions are available
        """
        # Note: Halo doesn't provide a direct API to check permissions
        # This is a placeholder for future implementation
        # For now, we assume permissions are valid if authentication succeeds
        logger.debug(f"Checking permissions: {required_permissions}")
        return True
    
    def get_session(self) -> requests.Session:
        """Get configured session for API calls."""
        return self.session 