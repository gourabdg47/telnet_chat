import asyncio
import sys
import logging

class ChatServer:
    def __init__(self):
        self.clients = {}
        self.topic = "GroupChat"
        self.server = None
        self.logger = logging.getLogger('ChatServer')
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        if not self.logger.handlers:
            # Create console handler and set level to debug
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)
            
         # Create file handler and set level to debug
        file_handler = logging.FileHandler('chat_server.log')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)  # Add file handler to the logger

    async def handle_client(self, reader, writer):
        try:
            writer.write(b"Enter your username: ")
            await writer.drain()
            username = (await reader.readuntil(b'\n')).decode().strip()
            self.logger.debug(f"New client connected: {username}.")

            welcome_message = f"Welcome, {username}! You've joined the group chat.\n"
            writer.write(welcome_message.encode())
            await writer.drain()

            self.clients[username] = writer

            while True:
                message = (await reader.readuntil(b'\n')).decode().strip()
                if message.lower() == "/exit":
                    writer.write(b"Goodbye!\n")
                    await writer.drain()
                    del self.clients[username]
                    break

                await self.broadcast_message(username, message)

        except asyncio.CancelledError:
            self.logger.debug("Client connection cancelled.")

        except Exception as e:
            self.logger.error(f"Exception occurred in handle_client: {e}")
            del self.clients[username]
            writer.close()
            await writer.wait_closed()

    async def broadcast_message(self, sender_username, message):
        formatted_message = f"{sender_username}: {message}\n"

        for client_username, client_writer in list(self.clients.items()):
            try:
                client_writer.write(formatted_message.encode())
                await client_writer.drain()

            except Exception as e:
                self.logger.error(f"Exception occurred while broadcasting message to {client_username}: {e}")
                del self.clients[client_username]
                client_writer.close()
                await client_writer.wait_closed()

    async def run_server(self):
        try:
            self.server = await asyncio.start_server(
                self.handle_client, '127.0.0.1', 8888
            )

            self.logger.info("Server started.")
            # await asyncio.sleep(120)  # Server runs for 2 minutes (120 seconds)
            while True:  # Run indefinitely
                await asyncio.sleep(1)  # Sleep to prevent blocking 

        except KeyboardInterrupt:
            pass

        except Exception as e:
            self.logger.error(f"Exception occurred in run_server: {e}")

        finally:
            await self.stop_server()

    async def stop_server(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()

        for client_username, client_writer in list(self.clients.items()):
            client_writer.close()
            await client_writer.wait_closed()
            del self.clients[client_username]

        asyncio.get_event_loop().stop()

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    chat_server = ChatServer()
    
    if sys.version_info >= (3, 7):
        asyncio.run(chat_server.run_server())
    else:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(chat_server.run_server())
        loop.close()
        
        # loop = asyncio.get_event_loop()
        # asyncio.ensure_future(chat_server.run_server())
        # loop.run_forever()
