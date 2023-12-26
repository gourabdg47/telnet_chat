import unittest
from app.chat_server import ChatServer

class TestChatServer(unittest.TestCase):

    def setUp(self):
        self.chat_server = ChatServer()

    def test_remove_client_by_username(self):
        # Add a test client
        client_writer = "test_writer"  
        self.chat_server.clients["test_user"] = client_writer
        
        # Call remove_client() with username
        self.chat_server.remove_client("test_user")
        
        # Verify client was removed
        self.assertNotIn("test_user", self.chat_server.clients)

    def test_remove_client_by_writer(self):
        # Add a test client
        client_writer = "test_writer"
        self.chat_server.clients["test_user"] = client_writer
        
        # Call remove_client() with writer 
        self.chat_server.remove_client(client_writer)
        
        # Verify client was removed
        self.assertNotIn("test_user", self.chat_server.clients)

    def test_broadcast_message(self):
        # Add 2 test clients
        client1_writer = "client1"
        client2_writer = "client2"
        self.chat_server.clients["user1"] = client1_writer
        self.chat_server.clients["user2"] = client2_writer

        # Call broadcast_message()
        self.chat_server.broadcast_message("user1", "test")

        # Verify message sent to all clients
        self.assertEqual(client1_writer.written, b"user1: test\n") 
        self.assertEqual(client2_writer.written, b"user1: test\n")

if __name__ == '__main__':
    unittest.main()
