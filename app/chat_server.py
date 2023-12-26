import asyncio
import sys
import logging

class ChatServer:
    def __init__(self):
        
        # Initialize running_tasks as an empty list
        self.running_tasks = []

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


    async def remove_client(self, client):
        """
        Remove a disconnected client from the server.

        Args:
            client: The client username or writer object to remove
        """

        if isinstance(client, str):
            writer = self.clients.get(client)
            if not writer:
                return

        else:
            writer = client
            client = None
            for c, w in self.clients.items():  
                if w == writer:
                    client = c
                    break

        # Log removal    
        self.logger.info(f"Removing client {client}")

        # Close writer connection
        writer.close()

        # Remove from clients dict
        if client:
            del self.clients[client]

        # Cancel any associated tasks
        tasks = [t for t in self.running_tasks if t.get_name() == client]
        for t in tasks:
            t.cancel()

        # Wait for cancellation to clean up resources 
        await asyncio.gather(*tasks, return_exceptions=True)

        async def ping_clients(self, clients):
            for client in clients:
                if await client.ping():
                    continue
                else:
                    self.remove_client(client)

    # async def handle_client(self, reader, writer):
    #     try:
    #         writer.write(b"Enter your username: ")
    #         await writer.drain()
    #         username = (await reader.readuntil(b'\n')).decode().strip()
    #         self.logger.debug(f"New client connected: {username}.")

    #         welcome_message = f"Welcome, {username}! You've joined the group chat.\n"
    #         writer.write(welcome_message.encode())
    #         await writer.drain()

    #         self.clients[username] = writer

    #         while True:
    #             message = (await reader.readuntil(b'\n')).decode().strip()
    #             if message.lower() == "/exit":
    #                 writer.write(b"Goodbye!\n")
    #                 # await writer.drain()
                    

    #                 try:
    #                     await asyncio.wait_for(writer.drain(), timeout=5)
    #                 except asyncio.TimeoutError:
    #                     # Log the timeout
    #                     self.logger.warning("Timeout occurred while waiting for client to drain")
                        
    #                     # Disconnect the client
    #                     self.clients.pop(username, None)
                        
    #                     # Close the writer
    #                     writer.close()
                        
    #                     # Cancel any pending tasks for this client
    #                     for task in self.running_tasks:
    #                         if task.get_name() == username:
    #                             task.cancel()
                            
    #                     # Log the disconnection  
    #                     self.logger.info(f"Disconnected client {username} due to timeout")


    #                 del self.clients[username]
    #                 break

    #             await self.broadcast_message(username, message)
            
    #         # Append the current task to running_tasks
    #         task = asyncio.current_task()
    #         self.running_tasks.append(task)

    #     except asyncio.CancelledError:
    #         self.logger.debug("Client connection cancelled.")

    #     except Exception as e:
    #         self.logger.error(f"Exception occurred in handle_client: {e}")
    #         del self.clients[username]
    #         writer.close()
    
    
    async def handle_client(self, reader, writer):
        
        writer.write(b"Enter your username: ")
        await writer.drain()

        username = (await reader.read(100)).decode().strip()
        self.clients[username] = (reader, writer, username)

        writer.write("Welcome !".encode())
        await writer.drain()

        while True:
            try:
                msg = await asyncio.wait_for(reader.readline(), timeout=60)
            
            except asyncio.TimeoutError:
                self.logger.warning(f"{username} timed out")
                break

            if msg.strip().decode() == "/exit":
                self.logger.info(f"{username} disconnected")
                break

            message = f"{username}: {msg.decode()}"
            await self.broadcast(message, username)

        del self.clients[username]
        writer.close()

    async def broadcast(self, message, sender):
        for username, (reader, writer, name) in self.clients.items():
            if name != sender:
                writer.write(message.encode())
                await writer.drain()




    # async def broadcast_message(self, sender_username, message):
    #     formatted_message = f"{sender_username}: {message}\n"

    #     for client_username, client_writer in list(self.clients.items()):
    #         try:
    #             client_writer.write(formatted_message.encode())
    #             await client_writer.drain()

    #         except Exception as e:
    #             self.logger.error(f"Exception occurred while broadcasting message to {client_username}: {e}")
    #             del self.clients[client_username]
    #             client_writer.close()


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

        # Cancel all client tasks
        for client_writer in self.clients.values():
            client_writer.close()

        await asyncio.gather(*[client_writer.drain() for client_writer in self.clients.values()])

        # Clear the clients dictionary
        self.clients.clear()

        print("self.running_tasks: ----> ", self.running_tasks)
        
        # Cancel all running tasks
        for task in self.running_tasks:
            task.cancel()

        await asyncio.gather(*self.running_tasks, return_exceptions=True)

        # Clear the running_tasks list
        self.running_tasks.clear()

        # Stop the event loop (if desired)
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
