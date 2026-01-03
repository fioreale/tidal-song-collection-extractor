"""Unit tests for authentication module."""

import unittest
from unittest.mock import MagicMock, patch

from src.tidal_extractor.auth import authenticate


class TestAuthentication(unittest.TestCase):
    """Test authentication functionality."""

    @patch("src.tidal_extractor.auth.tidalapi.Session")
    @patch("src.tidal_extractor.auth.console.print")
    def test_authenticate_success_silent(self, mock_print, mock_session_class):
        """Test successful authentication in silent mode."""
        # Create mock session and login objects
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_login = MagicMock()
        mock_login.verification_uri_complete = "https://example.com/auth"

        mock_future = MagicMock()
        mock_session.login_oauth.return_value = (mock_login, mock_future)
        mock_session.check_login.return_value = True

        # Call authenticate in silent mode
        result = authenticate(silent=True)

        # Verify session was returned
        self.assertIsNotNone(result)
        self.assertEqual(result, mock_session)

        # Verify login flow was called
        mock_session.login_oauth.assert_called_once()
        mock_future.result.assert_called_once()
        mock_session.check_login.assert_called_once()

        # Verify no console output in silent mode
        mock_print.assert_not_called()

    @patch("src.tidal_extractor.auth.tidalapi.Session")
    @patch("src.tidal_extractor.auth.console.print")
    def test_authenticate_success_verbose(self, mock_print, mock_session_class):
        """Test successful authentication with console output."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_login = MagicMock()
        mock_login.verification_uri_complete = "https://example.com/auth"

        mock_future = MagicMock()
        mock_session.login_oauth.return_value = (mock_login, mock_future)
        mock_session.check_login.return_value = True

        # Call authenticate in verbose mode
        result = authenticate(silent=False)

        # Verify session was returned
        self.assertIsNotNone(result)
        self.assertEqual(result, mock_session)

        # Verify console output was called (should print 3 messages)
        # 1. Authenticating panel
        # 2. Visit URL message
        # 3. Waiting message
        # 4. Success message
        self.assertEqual(mock_print.call_count, 4)

    @patch("src.tidal_extractor.auth.tidalapi.Session")
    @patch("src.tidal_extractor.auth.console.print")
    def test_authenticate_failure_check_login(self, mock_print, mock_session_class):
        """Test authentication failure when check_login returns False."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_login = MagicMock()
        mock_login.verification_uri_complete = "https://example.com/auth"

        mock_future = MagicMock()
        mock_session.login_oauth.return_value = (mock_login, mock_future)
        mock_session.check_login.return_value = False

        # Call authenticate
        result = authenticate(silent=False)

        # Verify None was returned
        self.assertIsNone(result)

        # Verify login failure message
        call_args = [str(call) for call in mock_print.call_args_list]
        output = "".join(call_args)
        self.assertIn("Login failed", output)

    @patch("src.tidal_extractor.auth.tidalapi.Session")
    @patch("src.tidal_extractor.auth.console.print")
    def test_authenticate_exception_verbose(self, mock_print, mock_session_class):
        """Test authentication when an exception occurs (verbose mode)."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        # Make login_oauth raise an exception
        mock_session.login_oauth.side_effect = Exception("Network error")

        # Call authenticate
        result = authenticate(silent=False)

        # Verify None was returned
        self.assertIsNone(result)

        # Verify error message was printed
        call_args = [str(call) for call in mock_print.call_args_list]
        output = "".join(call_args)
        self.assertIn("Authentication error", output)
        self.assertIn("Network error", output)

    @patch("src.tidal_extractor.auth.tidalapi.Session")
    @patch("src.tidal_extractor.auth.console.print")
    def test_authenticate_exception_silent(self, mock_print, mock_session_class):
        """Test authentication when an exception occurs (silent mode)."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        # Make login_oauth raise an exception
        mock_session.login_oauth.side_effect = Exception("Network error")

        # Call authenticate in silent mode
        result = authenticate(silent=True)

        # Verify None was returned
        self.assertIsNone(result)

        # Verify no console output in silent mode
        mock_print.assert_not_called()

    @patch("src.tidal_extractor.auth.tidalapi.Session")
    @patch("src.tidal_extractor.auth.console.print")
    def test_authenticate_future_timeout(self, mock_print, mock_session_class):
        """Test authentication when future.result() times out or fails."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_login = MagicMock()
        mock_login.verification_uri_complete = "https://example.com/auth"

        mock_future = MagicMock()
        mock_future.result.side_effect = Exception("Timeout waiting for authorization")

        mock_session.login_oauth.return_value = (mock_login, mock_future)

        # Call authenticate
        result = authenticate(silent=False)

        # Verify None was returned
        self.assertIsNone(result)

        # Verify error was handled
        call_args = [str(call) for call in mock_print.call_args_list]
        output = "".join(call_args)
        self.assertIn("Authentication error", output)

    @patch("src.tidal_extractor.auth.tidalapi.Session")
    def test_authenticate_returns_session_object(self, mock_session_class):
        """Test that authenticate returns a Session object on success."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_login = MagicMock()
        mock_login.verification_uri_complete = "https://example.com/auth"

        mock_future = MagicMock()
        mock_session.login_oauth.return_value = (mock_login, mock_future)
        mock_session.check_login.return_value = True

        result = authenticate(silent=True)

        # Verify result is the mock session object
        self.assertIs(result, mock_session)

    @patch("src.tidal_extractor.auth.tidalapi.Session")
    @patch("src.tidal_extractor.auth.console.print")
    def test_authenticate_default_silent_parameter(self, mock_print, mock_session_class):
        """Test that silent parameter defaults to False."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_login = MagicMock()
        mock_login.verification_uri_complete = "https://example.com/auth"

        mock_future = MagicMock()
        mock_session.login_oauth.return_value = (mock_login, mock_future)
        mock_session.check_login.return_value = True

        # Call authenticate without silent parameter
        authenticate()

        # Should print output (default is not silent)
        self.assertGreater(mock_print.call_count, 0)


if __name__ == "__main__":
    unittest.main()
